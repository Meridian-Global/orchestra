import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..app_layer.integrations.gmail_scanner import scan_inbox
from ..app_layer.integrations.linkedin_publisher import publish_to_linkedin

router = APIRouter()


class PublishLinkedInRequest(BaseModel):
    content: str
    access_token: str | None = None
    person_urn: str | None = None


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
