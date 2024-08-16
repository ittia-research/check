import os
import dspy

from modules import llm_long
from modules import Citation, LlamaIndexRM, Verdict

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
        
    def get(self, statement):
        with dspy.context(rm=self.retrieve):
            self.context_verdict = Verdict()
        
            # loading compiled Verdict
            optimizer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../optimizers/verdict_MIPROv2.json")
            self.context_verdict.load(optimizer_path)
            
            rep = self.context_verdict(statement)
        
        context = rep.context
        verdict = rep.answer

        # Use the LLM with higher token limit for citation generation call
        with dspy.context(lm=llm_long):
            rep = Citation()(statement=statement, context=context, verdict=verdict)
            citation = rep.citation

        return verdict, citation

