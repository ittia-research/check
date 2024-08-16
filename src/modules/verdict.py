import dspy
from dsp.utils import deduplicate

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
class Verdict(dspy.Module):
    def __init__(self, passages_per_hop=3, max_hops=3):
        super().__init__()
        # self.generate_query = dspy.ChainOfThought(GenerateSearchQuery)  # IMPORTANT: solves error `list index out of range`
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.generate_verdict = dspy.ChainOfThought(CheckStatementFaithfulness)
        self.max_hops = max_hops

    def forward(self, statement):
        context = []
        for hop in range(self.max_hops):
            query = self.generate_query[hop](context=context, statement=statement).query
            passages = self.retrieve(query).passages
            context = deduplicate(context + passages)

        verdict = self.generate_verdict(context=context, statement=statement)
        pred = dspy.Prediction(answer=verdict.verdict, rationale=verdict.rationale, context=context)
        return pred
 