import json
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..core.orchestrator import run_pipeline_stream

router = APIRouter()


class RunRequest(BaseModel):
    idea: str
    voice_profile: str = "default"


def sse(event: dict) -> str:
    """
    Format a dict as a properly structured Server-Sent Event message.

    SSE spec requires each field on its own line, terminated by a blank line:
      event: <event_name>
      data: <json_payload>
      <blank line>
    """
    name = event["event"]
    payload = json.dumps(event["data"])
    return f"event: {name}\ndata: {payload}\n\n"


@router.post("/api/run")
async def run_pipeline(req: RunRequest):
    """
    Stream pipeline execution as Server-Sent Events.

    Each event has shape: {"event": "<name>", "data": {...}}

    Events emitted in order:
      planner_started / planner_completed
      instagram_pass1_started / instagram_pass1_completed
      threads_pass1_started / threads_pass1_completed
      linkedin_pass1_started / linkedin_pass1_completed
      instagram_pass2_started / instagram_pass2_completed
      threads_pass2_started / threads_pass2_completed
      linkedin_pass2_started / linkedin_pass2_completed
      critic_started / critic_completed
      pipeline_completed
    """
    async def stream():
        # Note: pipeline calls are blocking (Claude API). Fine for single-user demo.
        for event in run_pipeline_stream(req.idea, req.voice_profile):
            yield sse(event)

    return StreamingResponse(stream(), media_type="text/event-stream")
