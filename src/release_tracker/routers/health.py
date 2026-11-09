from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from release_tracker.dependencies import SessionDep

router = APIRouter(tags=["meta"])

@router.get("/health", response_model=None, status_code=status.HTTP_200_OK)
def healthcheck(session: SessionDep) -> dict[str, str] | JSONResponse:
    # TODO: Use session.execute(text("SELECT 1")) to verify the database
    #       is reachable.
    #
    #       If the query succeeds, return {"status": "healthy"}.
    #       If it raises an exception, return a JSONResponse with
    #       {"status": "unhealthy"} and a 503 status code:
    #
    try:
        session.execute(text("SELECT 1"))
        return { "status": "healthy" }
    except Exception:
        return JSONResponse(
            {"status": "unhealthy"},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
