"""Health check routes"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.session import get_db

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
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check endpoint"""
    try:
        result = db.execute(text("SELECT 1 FROM DUAL")).scalar()
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
