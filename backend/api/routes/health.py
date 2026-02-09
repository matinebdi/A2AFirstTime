"""Health check routes"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "VacanceAI Backend",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    from database.oracle_client import execute_scalar

    try:
        result = execute_scalar("SELECT 1 FROM DUAL")
        db_status = "connected" if result == 1 else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"

    body = {
        "status": "ready" if db_status == "connected" else "not_ready",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

    if db_status != "connected":
        return JSONResponse(content=body, status_code=503)

    return body
