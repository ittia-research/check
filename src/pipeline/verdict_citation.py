import os
import concurrent.futures
import dspy
from llama_index.core import Document
from tenacity import retry, stop_after_attempt, wait_fixed
from urllib.parse import urlparse

import utils
from settings import settings
from modules import llm_long
from modules import Citation, LlamaIndexRM, ContextVerdict

# loading compiled ContextVerdict
optimizer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../optimizers/{settings.OPTIMIZER_FILE_NAME}")
context_verdict = ContextVerdict()  # IMPORTANT: needs to initiate before load
context_verdict.load(optimizer_path)

"""
All web pages of the same hostname as one source.
For each sources, get verdict and citation seperately.
"""
class VerdictCitation():
    def __init__(
        self,
        search_json,
    ):
        raw = search_json['data']
        self.data = {}  # main container
        self.update_retriever(raw)

    def update_retriever(self, raw):
        update_list = []
        
        # update doc
        for r in raw:
            url = r.get('url')
            url_hash = utils.get_md5(url)
            hostname = urlparse(url).hostname
            doc = utils.search_result_to_doc(r)
            self.data.setdefault(hostname, {}).setdefault('docs', {}).update({url_hash: {"doc": doc, "raw": r}})
            self.data[hostname]['new'] = True
            update_list.append(hostname) if hostname not in update_list else None

        # update retriever
        # TODO: what if we have a lot of small retriever to create and RM server latency high
        for hostname in update_list:
            docs = [v['doc'] for v in self.data[hostname]['docs'].values()]
            self.data[hostname]["retriever"] = LlamaIndexRM(docs=docs)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.5), before_sleep=utils.retry_log_warning, reraise=True)
    def _update_verdict_citation_single(self, hostname, statement):
        with dspy.context(rm=self.data[hostname]['retriever']):            
            rep = context_verdict(statement)
        
        context = rep.context
        verdict = rep.answer

        # Use the LLM with higher token limit for citation generation call
        with dspy.context(lm=llm_long):
            rep = Citation()(statement=statement, context=context, verdict=verdict)
            citation = rep.citation

        self.data[hostname]['statement'] = statement
        self.data[hostname]['context'] = context
        self.data[hostname]['verdict'] = verdict
        self.data[hostname]['citation'] = citation
        self.data[hostname]['new'] = False
        
    def update_verdict_citation(self, statement):
        with concurrent.futures.ThreadPoolExecutor(max_workers=settings.CONCURRENCY_VERDICT) as executor:
            futures = []
            for hostname in self.data:
                if self.data[hostname].get('new'):
                    futures.append(executor.submit(self._update_verdict_citation_single, hostname, statement))
            
            concurrent.futures.wait(futures)  # wait for all futures to complete
        
    """Get verdict and citation"""
    def get(self, statement):
        self.update_verdict_citation(statement)
        return self.data
