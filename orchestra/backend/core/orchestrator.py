"""
Orchestrator: coordinates multi-agent content generation with two-pass refinement.

Pass 1: Each agent generates initial output based on Brief
Pass 2: Each agent refines its output after seeing what others wrote
"""

from typing import Generator

from .context import AgentContext
from .voice_store import load_voice_profile
from ..agents.planner import PlannerAgent
from ..agents.instagram import InstagramAgent
from ..agents.threads import ThreadsAgent
from ..agents.linkedin import LinkedInAgent
from ..agents.critic import CriticAgent, CriticReview


def _show(agent_name: str, result, pass_label: str = ""):
    """Print agent thinking + output inline as pipeline runs."""
    label = f"{agent_name}{' · ' + pass_label if pass_label else ''}"
    print(f"\n┌─ [{label} Thinking]")
    for line in result.thinking.splitlines():
        print(f"│  {line}")
    print(f"└─ [{label} Output]")
    for line in result.output.splitlines():
        print(f"   {line}")


def run_pipeline_stream(idea: str, voice_profile_name: str = "default") -> Generator[dict, None, None]:
    """
    Generator version of the pipeline. Yields structured events for SSE streaming.
    Each event is a dict: {"event": "<name>", "data": {...}}
    """
    voice_profile = load_voice_profile(voice_profile_name)
    context = AgentContext()

    # Planner
    yield {"event": "planner_started", "data": {}}
    planner = PlannerAgent()
    context.brief = planner.run(idea=idea, voice_profile=voice_profile)
    yield {"event": "planner_completed", "data": {"brief": context.brief.to_dict()}}

    # Pass 1
    instagram_agent = InstagramAgent()
    threads_agent = ThreadsAgent()
    linkedin_agent = LinkedInAgent()

    yield {"event": "instagram_pass1_started", "data": {}}
    ig1 = instagram_agent.run(brief=context.brief)
    context.instagram_output = ig1.output
    yield {"event": "instagram_pass1_completed", "data": {"thinking": ig1.thinking, "output": ig1.output}}

    yield {"event": "threads_pass1_started", "data": {}}
    th1 = threads_agent.run(brief=context.brief, instagram_output=context.instagram_output)
    context.threads_output = th1.output
    yield {"event": "threads_pass1_completed", "data": {"thinking": th1.thinking, "output": th1.output}}

    yield {"event": "linkedin_pass1_started", "data": {}}
    li1 = linkedin_agent.run(brief=context.brief, instagram_output=context.instagram_output, threads_output=context.threads_output)
    context.linkedin_output = li1.output
    yield {"event": "linkedin_pass1_completed", "data": {"thinking": li1.thinking, "output": li1.output}}

    # Pass 2
    yield {"event": "instagram_pass2_started", "data": {}}
    ig2 = instagram_agent.run(brief=context.brief, threads_output=context.threads_output, linkedin_output=context.linkedin_output, is_refinement=True)
    context.instagram_output = ig2.output
    yield {"event": "instagram_pass2_completed", "data": {"thinking": ig2.thinking, "output": ig2.output}}

    yield {"event": "threads_pass2_started", "data": {}}
    th2 = threads_agent.run(brief=context.brief, instagram_output=context.instagram_output, linkedin_output=context.linkedin_output, is_refinement=True)
    context.threads_output = th2.output
    yield {"event": "threads_pass2_completed", "data": {"thinking": th2.thinking, "output": th2.output}}

    yield {"event": "linkedin_pass2_started", "data": {}}
    li2 = linkedin_agent.run(brief=context.brief, instagram_output=context.instagram_output, threads_output=context.threads_output, is_refinement=True)
    context.linkedin_output = li2.output
    yield {"event": "linkedin_pass2_completed", "data": {"thinking": li2.thinking, "output": li2.output}}

    # Critic
    yield {"event": "critic_started", "data": {}}
    critic = CriticAgent()
    critic_review = critic.run(
        brief=context.brief,
        instagram_output=context.instagram_output,
        threads_output=context.threads_output,
        linkedin_output=context.linkedin_output,
        voice_profile=voice_profile
    )
    yield {"event": "critic_completed", "data": {
        "notes": critic_review.notes,
        "instagram_improved": critic_review.instagram_improved,
        "threads_improved": critic_review.threads_improved,
        "linkedin_improved": critic_review.linkedin_improved,
    }}

    yield {"event": "pipeline_completed", "data": {
        "brief": context.brief.to_dict(),
        "instagram": context.instagram_output,
        "threads": context.threads_output,
        "linkedin": context.linkedin_output,
        "instagram_final": critic_review.instagram_improved,
        "threads_final": critic_review.threads_improved,
        "linkedin_final": critic_review.linkedin_improved,
        "critic_notes": critic_review.notes,
    }}


def run_full_pipeline(idea: str, voice_profile_name: str = "default") -> dict:
    """
    Run the complete multi-agent content generation pipeline.

    Args:
        idea: The content idea to develop
        voice_profile_name: Name of the voice profile to use

    Returns:
        dict with keys: brief, instagram, threads, linkedin, critic_review
    """
    voice_profile = load_voice_profile(voice_profile_name)
    context = AgentContext()

    # Step 1: Planner
    print("\n══════════════════════════════════════════════════")
    print("  PLANNER")
    print("══════════════════════════════════════════════════")
    planner = PlannerAgent()
    context.brief = planner.run(idea=idea, voice_profile=voice_profile)
    print(context.brief.to_string())

    # Step 2: First Pass
    print("\n══════════════════════════════════════════════════")
    print("  PASS 1 — Initial Generation")
    print("══════════════════════════════════════════════════")

    instagram_agent = InstagramAgent()
    ig1 = instagram_agent.run(brief=context.brief)
    _show("Instagram", ig1, "pass 1")
    context.instagram_output = ig1.output

    threads_agent = ThreadsAgent()
    th1 = threads_agent.run(brief=context.brief, instagram_output=context.instagram_output)
    _show("Threads", th1, "pass 1")
    context.threads_output = th1.output

    linkedin_agent = LinkedInAgent()
    li1 = linkedin_agent.run(brief=context.brief, instagram_output=context.instagram_output, threads_output=context.threads_output)
    _show("LinkedIn", li1, "pass 1")
    context.linkedin_output = li1.output

    # Step 3: Second Pass
    print("\n══════════════════════════════════════════════════")
    print("  PASS 2 — Refinement with full context")
    print("══════════════════════════════════════════════════")

    ig2 = instagram_agent.run(brief=context.brief, threads_output=context.threads_output, linkedin_output=context.linkedin_output, is_refinement=True)
    _show("Instagram", ig2, "pass 2")
    context.instagram_output = ig2.output

    th2 = threads_agent.run(brief=context.brief, instagram_output=context.instagram_output, linkedin_output=context.linkedin_output, is_refinement=True)
    _show("Threads", th2, "pass 2")
    context.threads_output = th2.output

    li2 = linkedin_agent.run(brief=context.brief, instagram_output=context.instagram_output, threads_output=context.threads_output, is_refinement=True)
    _show("LinkedIn", li2, "pass 2")
    context.linkedin_output = li2.output

    # Step 4: Critic
    print("\n══════════════════════════════════════════════════")
    print("  CRITIC")
    print("══════════════════════════════════════════════════")
    critic = CriticAgent()
    critic_review = critic.run(
        brief=context.brief,
        instagram_output=context.instagram_output,
        threads_output=context.threads_output,
        linkedin_output=context.linkedin_output,
        voice_profile=voice_profile
    )

    return {
        "brief": context.brief,
        "instagram": context.instagram_output,
        "threads": context.threads_output,
        "linkedin": context.linkedin_output,
        "critic_review": critic_review
    }
