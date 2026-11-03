import logging
import time
from typing import Annotated

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from .config import configure_logging, get_settings
from .database import get_session
from .routers import projects

configure_logging(debug=get_settings().debug)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Release Tracker API",
    description="An API for tracking project milestones and developer tasks.",
)

# @app.middleware("http")
# async def my_middleware(request: Request, call_next):
#     # Pre-route work happens here (before the endpoint is called)
#     response = await call_next(request)
#     # Post-route work happends here (after the endpoint finishes)
#     return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s completed in %.2fms with status code %s",
        request.method,
        request.url.path,
        process_time,
        response.status_code
    )
    return response


app.include_router(projects.router)

SessionDep = Annotated[Session, Depends(get_session)]


def slugify(value: str) -> str:
    cleaned = "".join(c for c in value.lower() if c.isalnum() or c == " ")
    return "-".join(cleaned.split()) or "project"

@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "Data conflict occured (e.g., duplicate entry)."
        }
    )

@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "app": "Release Tracker API",
        "docs": "/docs",
        "health": "/health",
    }