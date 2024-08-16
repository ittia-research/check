import dspy
import logging

"""Notes: LLM will choose a direction based on known facts"""
class GenerateSearchEngineQuery(dspy.Signature):
    """Write a search engine query that will help retrieve info related to the statement."""
    statement = dspy.InputField()
    query = dspy.OutputField()
    
class SearchQuery(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_query = dspy.ChainOfThought(GenerateSearchEngineQuery)

    def forward(self, statement):
        query = self.generate_query(statement=statement)
        logging.info(f"DSPy CoT search query: {query}")
        return query.query