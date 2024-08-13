import dspy
from dsp.utils import deduplicate

from retrieve import LlamaIndexRM
from settings import settings

llm = dspy.OpenAI(model=settings.LLM_MODEL_NAME, api_base=f"{settings.OPENAI_BASE_URL}/", max_tokens=200, stop='\n\n')
dspy.settings.configure(lm=llm)

class CheckStatementFaithfulness(dspy.Signature):
    """Verify that the statement is based on the provided context."""
    context = dspy.InputField(desc="facts here are assumed to be true")
    statement = dspy.InputField()
    verdict = dspy.OutputField(desc="True/False/Irrelevant indicating if statement is faithful to context")
    
class GenerateSearchQuery(dspy.Signature):
    """Write a simple search query that will help retrieve info related to the statement."""
    context = dspy.InputField(desc="may contain relevant facts")
    statement = dspy.InputField()
    query = dspy.OutputField()

class GenerateCitedParagraph(dspy.Signature):
    """Generate a paragraph with citations."""
    context = dspy.InputField(desc="may contain relevant facts")
    statement = dspy.InputField()
    verdict = dspy.InputField()
    paragraph = dspy.OutputField(desc="includes citations")

"""
SimplifiedBaleen module
Avoid unnecessary content in module cause MIPROv2 optimizer will analize modules.

Args:
    retrieve: dspy.Retrieve
    
To-do: 
  - retrieve latest facts
  - remove some contexts incase token reaches to max
  - does different InputField name other than answer compateble with dspy evaluate
"""
class ContextVerdict(dspy.Module):
    def __init__(self, retrieve, passages_per_hop=3, max_hops=3):
        super().__init__()
        # self.generate_query = dspy.ChainOfThought(GenerateSearchQuery)  # IMPORTANT: solves error `list index out of range`
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = retrieve
        self.retrieve.k = passages_per_hop
        self.generate_verdict = dspy.ChainOfThought(CheckStatementFaithfulness)
        self.max_hops = max_hops

    def forward(self, statement):
        context = []
        for hop in range(self.max_hops):
            query = self.generate_query[hop](context=context, statement=statement).query
            passages = self.retrieve(query=query, text_only=True)
            context = deduplicate(context + passages)

        verdict = self.generate_verdict(context=context, statement=statement)
        pred = dspy.Prediction(answer=verdict.verdict, rationale=verdict.rationale, context=context)
        return pred

"""Generate citation from context and verdict"""
class Citation(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_cited_paragraph = dspy.ChainOfThought(GenerateCitedParagraph)

    def forward(self, statement, context, verdict):
        citation = self.generate_cited_paragraph(context=context, statement=statement, verdict=verdict)
        pred = dspy.Prediction(verdict=verdict, citation=citation.paragraph, context=context)
        return pred

"""
Get both verdict and citation.

Args:
    retrieve: dspy.Retrieve
"""
class VerdictCitation():
    def __init__(
        self,
        docs,
    ):
        self.retrieve = LlamaIndexRM(docs=docs)
        
        # loading compiled ContextVerdict
        self.context_verdict = ContextVerdict(retrieve=self.retrieve)
        self.context_verdict.load("./optimizers/verdict_MIPROv2.json")

    def get(self, statement):
        rep = self.context_verdict(statement)
        context = rep.context
        verdict = rep.answer
        
        rep = Citation()(statement=statement, context=context, verdict=verdict)
        citation = rep.citation

        return verdict, citation
        