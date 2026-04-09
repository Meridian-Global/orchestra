import json
import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from ..core.orchestrator import run_pipeline_stream
from ..integrations.gmail_scanner import scan_inbox
from ..integrations.linkedin_publisher import publish_to_linkedin

router = APIRouter()


class RunRequest(BaseModel):
    idea: str
    voice_profile: str = "default"


class PublishLinkedInRequest(BaseModel):
    content: str
    access_token: str | None = None
    person_urn: str | None = None


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


@router.post("/api/publish/linkedin")
async def publish_linkedin(req: PublishLinkedInRequest):
    access_token = req.access_token or os.getenv("LINKEDIN_ACCESS_TOKEN")
    person_urn = req.person_urn or os.getenv("LINKEDIN_PERSON_URN")

    if not access_token or not person_urn:
        raise HTTPException(status_code=401, detail="LinkedIn credentials not configured")

    result = publish_to_linkedin(
        content=req.content,
        access_token=access_token,
        person_urn=person_urn,
    )

    if result["success"]:
        return {"post_id": result["post_id"], "error": None}

    return JSONResponse(status_code=502, content={"post_id": None, "error": result["error"]})


@router.get("/api/ideas/scan")
async def scan_gmail_ideas(max_results: int = Query(default=20, ge=1, le=50)):
    try:
        return scan_inbox(max_results=max_results)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
