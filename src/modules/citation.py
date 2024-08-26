import dspy

class GenerateCitedParagraph(dspy.Signature):
    """Generate a paragraph with citations."""
    context = dspy.InputField(desc="May contain relevant facts.")
    statement = dspy.InputField()
    verdict = dspy.InputField()
    paragraph = dspy.OutputField(desc="Includes citations.")
    
"""Generate citation from context and verdict"""
class Citation(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_cited_paragraph = dspy.ChainOfThought(GenerateCitedParagraph)

    def forward(self, statement, context, verdict):
        citation = self.generate_cited_paragraph(context=context, statement=statement, verdict=verdict)
        pred = dspy.Prediction(verdict=verdict, citation=citation.paragraph, context=context)
        return pred
