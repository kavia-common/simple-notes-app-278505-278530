from __future__ import annotations

import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .logging_config import configure_logging
from .routers_notes import router as notes_router

# Configure logging as early as possible
configure_logging()

openapi_tags = [
    {
        "name": "Health",
        "description": "Healthcheck and operational endpoints.",
    },
    {
        "name": "Notes",
        "description": "CRUD operations for Notes.",
    },
]

app = FastAPI(
    title="Simple Notes API",
    description="A simple, secure Notes CRUD API using FastAPI.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# CORS: derive allowed origins from environment to be safe by default
# If not provided, default to '*', but recommend setting explicit origins.
default_origins = os.getenv("REACT_APP_FRONTEND_URL", "*")
allow_origins: List[str] = [o.strip() for o in default_origins.split(",") if o.strip()] if default_origins else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Returns health status of the API service.",
)
def health_check() -> dict:
    """Health check endpoint returning a simple JSON status."""
    return {"message": "Healthy"}


# Register routers
app.include_router(notes_router)
