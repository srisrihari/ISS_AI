from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.models.database import get_db
from app.models.schemas import LogResponse
from app.services.log_service import LogService

router = APIRouter()

@router.get("/logs", response_model=LogResponse)
def get_logs(
    startDate: str = Query(..., description="Start date in ISO format"),
    endDate: str = Query(..., description="End date in ISO format"),
    itemId: Optional[str] = Query(None, description="Filter by item ID"),
    userId: Optional[str] = Query(None, description="Filter by user ID"),
    actionType: Optional[str] = Query(None, description="Filter by action type"),
    db: Session = Depends(get_db)
):
    """
    Get logs filtered by various criteria.
    """
    try:
        log_service = LogService()
        logs = log_service.get_logs(startDate, endDate, itemId, userId, actionType)
        
        return LogResponse(logs=logs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")
