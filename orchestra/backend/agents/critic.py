from .base import BaseAgent
from ..core.brief import Brief
import json
from dataclasses import dataclass


@dataclass
class CriticReview:
    """
    Critic's review with cross-platform analysis and improved versions.
    """
    notes: str  # cross-platform analysis: duplicates, off-brand, weak spots
    instagram_original: str
    instagram_improved: str
    threads_original: str
    threads_improved: str
    linkedin_original: str
    linkedin_improved: str


class CriticAgent(BaseAgent):
    """
    Reviews all platform outputs together.
    Flags duplicated angles, off-brand tone, weak hooks/endings.
    Rewrites with specific improvements, not generic advice.
    """

    def __init__(self):
        super().__init__(name="Critic")

    def build_prompt(self, brief: Brief, instagram_output: str, threads_output: str, linkedin_output: str, voice_profile: dict) -> str:
        avoid_phrases = ", ".join(f'"{p}"' for p in voice_profile.get("content_rules", {}).get("avoid_phrases", []))
        voice_not = ", ".join(voice_profile.get("voice", {}).get("not", []))
        voice_adj = ", ".join(voice_profile.get("voice", {}).get("adjectives", []))

        return f"""You are a sharp brand voice editor reviewing three platform posts written for the same idea.

{brief.to_string()}

BRAND VOICE:
- Tone should be: {voice_adj}
- Never sound: {voice_not}
- Avoid phrases: {avoid_phrases}
- Signature moves: lead with specific observation, show the work, end with question or next step

=== INSTAGRAM ===
{instagram_output}

=== THREADS ===
{threads_output}

=== LINKEDIN ===
{linkedin_output}

STEP 1 — CROSS-PLATFORM ANALYSIS (be specific, not generic):
Look at all three posts together and identify:
1. Duplicated angles: are two posts making the same point or using the same hook?
2. Off-brand moments: specific lines that sound corporate, preachy, or guru-ish
3. Weak hooks or endings: which post opens or closes weakly, and exactly why

STEP 2 — REWRITE each post to fix the issues you found:
- Cut hedging language ("kind of", "maybe", "sometimes")
- Cut explanatory sentences that tell instead of show
- Cut business-speak and preachy takeaways
- Make each post's angle distinct from the others
- Keep hashtags specific or remove them entirely
- Shorten by at least 15%

Return ONLY valid JSON with this exact structure:
{{
  "notes": "2-4 sentences: what you found across all three posts — specific issues, not generic feedback",
  "instagram_improved": "improved instagram caption here",
  "threads_improved": "improved threads post here",
  "linkedin_improved": "improved linkedin post here"
}}

Return ONLY the JSON, no other text.
"""

    def run(self, brief: Brief, instagram_output: str, threads_output: str, linkedin_output: str, voice_profile: dict) -> CriticReview:
        prompt = self.build_prompt(
            brief=brief,
            instagram_output=instagram_output,
            threads_output=threads_output,
            linkedin_output=linkedin_output,
            voice_profile=voice_profile
        )
        response = self.generate(prompt, max_tokens=6000)

        # Strip markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        try:
            improved_data = json.loads(response)
        except json.JSONDecodeError:
            try:
                improved_data = json.loads(response, strict=False)
            except json.JSONDecodeError as e:
                raise ValueError(f"Critic did not return valid JSON. Error: {e}. Response: {response[:500]}")

        try:
            return CriticReview(
                notes=improved_data.get("notes", ""),
                instagram_original=instagram_output,
                instagram_improved=improved_data["instagram_improved"],
                threads_original=threads_output,
                threads_improved=improved_data["threads_improved"],
                linkedin_original=linkedin_output,
                linkedin_improved=improved_data["linkedin_improved"]
            )
        except KeyError as e:
            raise ValueError(f"Critic JSON missing required key: {e}. Response keys: {improved_data.keys()}")
