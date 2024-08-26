import dspy
import re
from dsp.utils import deduplicate

class CheckStatement(dspy.Signature):
    """Verify the statement based on the provided context."""
    context = dspy.InputField(desc="Facts here are assumed to be true.")
    statement = dspy.InputField()
    verdict = dspy.OutputField(desc=(
                                    "In order,"
                                    " `False` if the context directly negates the statement,"
                                    " `True` if it directly supports the statement,"
                                    " else `Irrelevant`.")
                              )


"""
LM sometimes reply additional words after the verdict, this function address the issue.
"""
def extract_verdict(input):
    # Extract the first word
    match = re.match(r'\s*(\w+)', input)
    if match:
        first_word = match.group(1)
        if first_word.lower() in ['false', 'true', 'irrelevant']:
            # Return verdict with the first letter capitalized
            return first_word.capitalize()
    # If no in the verdict list, return the input directly
    return input
    
class GenerateSearchQuery(dspy.Signature):
    """Write a search query that will help retrieve additional info related to the statement."""
    context = dspy.InputField(desc="Existing context.")
    statement = dspy.InputField()
    query = dspy.OutputField()
    
"""
SimplifiedBaleen module
Avoid unnecessary content in module cause MIPROv2 optimizer will analize modules.

To-do: 
  - retrieve latest facts
  - query results might stays the same in hops: better retrieval
"""
class Verdict(dspy.Module):
    def __init__(self, passages_per_hop=3, max_hops=3):
        super().__init__()
        # self.generate_query = dspy.ChainOfThought(GenerateSearchQuery)  # IMPORTANT: solves error `list index out of range`
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.generate_verdict = dspy.ChainOfThought(CheckStatement)
        self.max_hops = max_hops

    def forward(self, statement):
        context = []
        for hop in range(self.max_hops):
            query = self.generate_query[hop](context=context, statement=statement).query
            passages = self.retrieve(query).passages
            context = deduplicate(context + passages)

        _verdict_predict = self.generate_verdict(context=context, statement=statement)
        verdict = extract_verdict(_verdict_predict.verdict)
        pred = dspy.Prediction(answer=verdict, rationale=_verdict_predict.rationale, context=context)
        return pred