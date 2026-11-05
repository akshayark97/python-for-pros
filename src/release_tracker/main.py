import logging
import time
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .config import configure_logging, get_settings
from .routers import projects, tasks

configure_logging(debug=get_settings().debug)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Release Tracker API",
    description="An API for tracking project milestones and developer tasks.",
)

app.include_router(projects.router)
app.include_router(tasks.router)


@app.exception_handler(IntegrityError)
def handle_integrity_error(request: Request, exc: IntegrityError):
    logger.warning(
        "IntegrityError handled method=%s path=%s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Data conflict occurred (e.g., duplicate entry)."},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next: Any) -> Any:
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    logger.info(
        "%s %s completed in %.2fms with status code %s",
        request.method,
        request.url.path,
        process_time,
        response.status_code,
    )
    return response


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "app": "Release Tracker API",
        "docs": "/docs",
    }