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

app = FastAPI(title="Orchestra API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)
