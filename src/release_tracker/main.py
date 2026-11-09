import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError

from . import __version__
from .config import configure_logging, get_settings
from .routers import auth, health, projects, tasks

APP_NAME = "Release Tracker API"
logger = logging.getLogger(__name__)
static_dir = Path(__file__).resolve().parent / "static"

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    configure_logging(debug=get_settings().debug)
    yield

app = FastAPI(
    title=APP_NAME,
    version=__version__,
    description="An API for tracking project milestones and developer tasks.",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.exception_handler(IntegrityError)
def handle_integrity_error(
    request: Request, exc: IntegrityError
) -> JSONResponse:
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

app.mount("/app/static", StaticFiles(directory=static_dir), name="app-static")

@app.get("/app", include_in_schema=False)
@app.get("/app/", include_in_schema=False)
def frontend_dashboard() -> FileResponse:
    logger.info("Serving dashboard")
    return FileResponse(static_dir / "index.html")


@app.get("/", tags=["meta"])
def read_root() -> dict[str, str]:
    logger.debug("Serving root metadata")
    return {
        "app": APP_NAME,
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }
