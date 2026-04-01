from .base import BaseAgent, AgentOutput
from ..core.brief import Brief
from typing import Optional


class LinkedInAgent(BaseAgent):
    """
    Generates LinkedIn content based on Brief.
    Can see other agents' outputs to react and differentiate.
    """

    def __init__(self):
        super().__init__(name="LinkedIn")

    def build_prompt(self, brief: Brief, instagram_output: Optional[str] = None, threads_output: Optional[str] = None, is_refinement: bool = False) -> str:
        prompt = f"""You are a LinkedIn content writer.

{brief.to_string()}

PLATFORM CONTEXT:
LinkedIn prioritizes:
- Professional but human tone
- Insights, lessons, or frameworks
- Storytelling with a takeaway
- Longer-form content accepted
- Industry-relevant context
- Value-driven, not self-promotional
"""

        if instagram_output or threads_output:
            prompt += "\nOTHER AGENTS WROTE:\n"
            if instagram_output:
                prompt += f"\nINSTAGRAM:\n{instagram_output}\n"
            if threads_output:
                prompt += f"\nTHREADS:\n{threads_output}\n"
            prompt += "\nReact to the above: take a different angle, don't repeat their hook or structure.\n"

        if is_refinement:
            prompt += "\nThis is your refinement pass. Tighten and differentiate — make it unmistakably LinkedIn-native.\n"

        prompt += "\nWrite the LinkedIn post. Be specific and true to the brand voice."
        return prompt

    def run(self, brief: Brief, instagram_output: Optional[str] = None, threads_output: Optional[str] = None, is_refinement: bool = False) -> AgentOutput:
        prompt = self.build_prompt(
            brief=brief,
            instagram_output=instagram_output,
            threads_output=threads_output,
            is_refinement=is_refinement
        )
        return self.generate_with_thinking(prompt)
