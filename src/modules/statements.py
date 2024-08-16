import dspy
import logging
from pydantic import BaseModel, Field
from typing import List

# references: https://github.com/weaviate/recipes/blob/main/integrations/llm-frameworks/dspy/4.Structured-Outputs-with-DSPy.ipynb
class Output(BaseModel):
    statements: List = Field(description="A list of key statements")
    
# TODO: test consistency especially when content contains false claims
class GenerateStatements(dspy.Signature):
    """Extract the original statements from given content without fact check."""
    content: str = dspy.InputField(desc="The content to summarize")
    output: Output = dspy.OutputField()

class Statements(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_statements = dspy.TypedChainOfThought(GenerateStatements, max_retries=6)

    def forward(self, content):
        statements = self.generate_statements(content=content)
        logging.info(f"DSPy CoT statements: {statements}")
        return statements.output.statements