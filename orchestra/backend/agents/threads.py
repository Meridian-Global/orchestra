from .base import BaseAgent, AgentOutput
from ..core.brief import Brief
from typing import Optional


class ThreadsAgent(BaseAgent):
    """
    Generates Threads content based on Brief.
    Can see other agents' outputs to react and differentiate.
    """

    def __init__(self):
        super().__init__(name="Threads")

    def build_prompt(self, brief: Brief, instagram_output: Optional[str] = None, linkedin_output: Optional[str] = None, is_refinement: bool = False) -> str:
        prompt = f"""You are a Threads content writer.

{brief.to_string()}

PLATFORM CONTEXT:
Threads prioritizes:
- Conversational, casual tone
- Quick, digestible thoughts
- Often more raw/unpolished than Instagram
- Can be a single thought or short thread
- Less focus on hashtags
- Direct engagement with the idea
"""

        if instagram_output or linkedin_output:
            prompt += "\nOTHER AGENTS WROTE:\n"
            if instagram_output:
                prompt += f"\nINSTAGRAM:\n{instagram_output}\n"
            if linkedin_output:
                prompt += f"\nLINKEDIN:\n{linkedin_output}\n"
            prompt += "\nReact to the above: take a different angle, don't repeat their hook or structure.\n"

        if is_refinement:
            prompt += "\nThis is your refinement pass. Tighten and differentiate — make it unmistakably Threads-native.\n"

        prompt += "\nWrite the Threads post. Be specific and true to the brand voice."
        return prompt

    def run(self, brief: Brief, instagram_output: Optional[str] = None, linkedin_output: Optional[str] = None, is_refinement: bool = False) -> AgentOutput:
        prompt = self.build_prompt(
            brief=brief,
            instagram_output=instagram_output,
            linkedin_output=linkedin_output,
            is_refinement=is_refinement
        )
        return self.generate_with_thinking(prompt)
