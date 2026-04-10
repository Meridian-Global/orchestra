"""
Orchestra FastAPI app.

Run with:
  uvicorn orchestra.backend.main:app --reload
from the repo root, or:
  uvicorn backend.main:app --reload
from the orchestra/ directory.
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .api.integrations_routes import router as integrations_router

app = FastAPI(title="Orchestra API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(integrations_router)
