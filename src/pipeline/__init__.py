import asyncio
import dspy
import logging
import os
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from tenacity import retry, stop_after_attempt, wait_fixed
from urllib.parse import urlparse

import utils
from api import ReadUrl, SearchWeb
from modules import SearchQuery, Statements
from modules import llm_long, Citation, LlamaIndexRM, ContextVerdict
from settings import settings

# loading compiled ContextVerdict
optimizer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../optimizers/{settings.OPTIMIZER_FILE_NAME}")
context_verdict = ContextVerdict()
context_verdict.load(optimizer_path)

class Check():
    """
    Run the full cycle from raw input to verdicts of multiple statements.
    Keep data in the class.

    Exception handle:
      - Mark doc as invalid if failed to read content.
      
    TODO:
      - Add support of verdict standards.
      - Make better use of the other data of web search.
      - Generate or draw class data structure.
    """

    def __init__(self, input: str, format: str = 'markdown'):
        """
        Args:
          - input: raw input to check
          - format: markdown | json, format of the returning response

        Notes: avoid run I/O intense functions here to better support async
        """
        self.input = input
        self.format = format
        self.data = {}  # contains all intermediate and final data

    async def final(self):
        await self.get_statements()
        _task = [asyncio.create_task(self._pipe_statement(data_statement)) for data_statement in self.data.values()]
        await asyncio.gather(*_task)

        # List of all summaries
        summaries = [v['summary'] for v in self.data.values()]

        # Update reports
        if self.format == 'json':
            self.reports = {
                'input': self.input,
                'summaries': summaries,
            }
        else:
            self.reports = utils.generate_report_markdown(self.input, summaries)

        return self.reports
        
    async def _pipe_statement(self, data_statement):
        """
        Pipeline to process single statement.
        Get all links to generate hostname mapping before fetch content and generate verdict citation for each hostname(source).

        TODO:
          - Make unit works on URL instead of hostname level.
        """
        await self.get_search_query(data_statement)
        _updated_sources = await self.update_source_map(data_statement['sources'], data_statement['query'])
        _task = [asyncio.create_task(self._pipe_source(data_statement['sources'][source], data_statement['statement'])) for source in _updated_sources]
        await asyncio.gather(*_task)

        # update summary
        self.update_summary(data_statement)

    async def _pipe_source(self, data_source, statement):
        """Update docs and then update retriever, verdict, citation"""
        
        # update docs
        _task_docs = []
        for _, data_doc in data_source['docs'].items():
            if not data_doc.get('doc') and data_doc.get('valid') is not False:  # TODO: better way to decide if update doc
                _task_docs.append(asyncio.create_task(self.update_doc(data_doc)))
        await asyncio.gather(*_task_docs)  # finish all docs processing

        # update retriever
        docs = [v['doc'] for v in data_source['docs'].values() if v.get('valid') is not False]
        if docs:
            data_source["retriever"] = await run_in_threadpool(LlamaIndexRM, docs=docs)
            
            # update verdict, citation
            await run_in_threadpool(self.update_verdict_citation, data_source, statement)
        else:
            data_source['valid'] = False  # TODO: update status after add valid doc
                
    # Statements has retry set already, do not retry here
    async def get_statements(self):
        """Get list of statements from a text string"""
        try:
            _dspy = Statements()
            self.statements = await run_in_threadpool(_dspy, self.input)
        except Exception as e:
            logging.error(f"Get statements failed: {e}")
            self.statements = []

        if not self.statements:
            raise HTTPException(status_code=500, detail="No statements found")
        self.statements = self.statements[:2]  # TODO: limiting max statements to 2 since haven't support long input yet.
        logging.info(f"statements: {self.statements}")
        
        # add statements to data with order
        for i, v in enumerate(self.statements, start=1):
            _key = utils.get_md5(v)
            self.data.setdefault(_key, {'order': i, 'statement': v, 'sources': {}})

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.1), before_sleep=utils.retry_log_warning, reraise=True)
    async def get_search_query(self, data_statement):
        """Get search query for one statement and add to the data"""
        _dspy = SearchQuery()
        data_statement['query'] = await run_in_threadpool(_dspy, data_statement['statement'])

    async def update_source_map(self, data_sources, query):
        """
        Update map of sources(web URLs for now),
        add to the data and return list of updated sources.
        """
        _updated = []
        _search_web = SearchWeb(query=query)
        async for url_dict in _search_web.get():
            url = url_dict.get('url')
            if not url:  # TODO: necessary?
                continue
            url_hash = utils.get_md5(url)
            hostname = urlparse(url).hostname
            data_sources.setdefault(hostname, {}).setdefault('docs', {}).update({url_hash: {'url': url}})
            _updated.append(hostname) if hostname not in _updated else None
        return _updated

    async def update_doc(self, data_doc):
        """Update doc (URL content for now)"""
        try:
            _read_url = ReadUrl(url=data_doc['url'])
            _rep = await _read_url.get()
            
            # check source read `status` and content
            if _rep['status'] != 'ok' or not _rep['content']:
                raise Exception
        except Exception:
            data_doc['valid'] = False
            logging.warning(f"Failed to read URL, mark as invalid: {data_doc['url']}")
            return
        data_doc['raw'] = _rep  # dict including URL content and metadata, etc.
        data_doc['title'] = _rep['title']
        data_doc['doc'] = utils.search_result_to_doc(_rep)  # TODO: better process

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.5), before_sleep=utils.retry_log_warning, reraise=True)
    def update_verdict_citation(self, data_source, statement):
        """Update a single source"""

        with dspy.context(rm=data_source['retriever']):            
            rep = context_verdict(statement)
        
        context = rep.context
        verdict = rep.answer

        # Use the LLM with higher token limit for citation generation call
        with dspy.context(lm=llm_long):
            rep = Citation()(statement=statement, context=context, verdict=verdict)
            citation = rep.citation

        data_source['context'] = context
        data_source['verdict'] = verdict
        data_source['citation'] = citation

    def update_summary(self, data_statement):
        """
        Calculate and summarize the verdicts of multiple sources.
        Choose the one verdict with highest weight and use its citation as final.

        Introduce some weights:
          - total: the number of total verdicts
          - valid: the number of verdicts in the desired categories
          - winning: the count of the winning verdict
          - and count of verdicts of each desired categories

        Response:
            Verdicts:
                - true
                - false
                - irrelevant
                - tie: number of true and false verdicts are the same and above zero
                - None: no valid verdict found

        Exceptions:
          - If no valid verdicts, generate summary with statement but verdict related keys set to None.

        TODO: maybe output all citations instead of the winning one only.
        """

        statement = data_statement['statement']

        # initialize summary
        data_summary = data_statement['summary'] = {
            "statement": statement,
            "verdict": None,
            "weights": {}, 
            "citations": {}, 
        }
        
        weight_total = 0
        weight_valid = 0
        sum_score = 0
        sum_citation = {
            "true": {"citations": [], "weight": 0},
            "false": {"citations": [], "weight": 0},
            "irrelevant": {"citations": [], "weight": 0},
        }
    
        for hostname, source in data_statement['sources'].items():
            # skip invalid source
            if source.get('valid') is False:
                continue

            # generate citations, add to groups, calculate weights
            weight_total += 1
            v = source['verdict'].lower()
            if v in sum_citation:  # Checking if verdict are valid here, do not add non-valid verdict to sum_citation keys prior
                weight_valid += 1
                citation = {
                    'citation': source['citation'],
                    'source': f"http://{hostname}",
                  }
                sum_citation[v]['citations'].append(citation)
                sum_citation[v]['weight'] += 1
                if v == 'true':
                    sum_score += 1
                elif v == 'false':
                    sum_score -= 1

        # Return None if no valid verdict found
        if weight_valid == 0:
            logging.warning(f"No valid verdict found for statement: {statement}")
            return  # return with verdicts None
    
        """
        Get the final verdict.

        TODO:
            - Some source should have different weights. For example:
              - A well-known reliable source compare to a average one.
              - One has more latest info and the statement is time sensitive.
        """
        if sum_score > 0:
            verdict = "true"
        elif sum_score < 0:
            verdict = "false"
        else:
            # If positive/negative verdict are not 0, set verdict to tie.
            if sum_citation['true']['weight'] > 0:
                verdict = 'tie'
                sum_citation['tie'] = {"citations": [], "weight": 0}  # add keys for processing after
            else:
                verdict = "irrelevant"
        data_summary['verdict'] = verdict
    
        # add all weights to the summary
        data_summary['weights'] = {"total": weight_total, "valid": weight_valid, "winning": sum_citation[verdict]['weight']}
        for key in sum_citation.keys():
            data_summary['weights'][key] = sum_citation[key]['weight']
            
        # Gather all non-empty citations
        for key, value in sum_citation.items():
            if value['citations']:
                data_summary['citations'][key] = value['citations']
