from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional

from ..models.database import get_db
from ..services.emergency_service import EmergencyService

router = APIRouter()

@router.get("/emergency/critical-items", response_model=List[Dict])
def get_critical_items(db: Session = Depends(get_db)):
    """
    Get a list of critical items (high priority) and their accessibility status.
    """
    try:
        emergency_service = EmergencyService()
        critical_items = emergency_service.identify_critical_items()
        return critical_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error identifying critical items: {str(e)}")

@router.post("/emergency/optimize-access", response_model=Dict)
def optimize_emergency_access(db: Session = Depends(get_db)):
    """
    Optimize the positions of critical items to ensure they are easily accessible in emergencies.
    """
    try:
        emergency_service = EmergencyService()
        result = emergency_service.optimize_emergency_access()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error optimizing emergency access: {str(e)}")

@router.post("/emergency/declare", response_model=Dict)
def declare_emergency(emergency_type: str, affected_zones: Optional[List[str]] = None, db: Session = Depends(get_db)):
    """
    Declare an emergency and get quick access plans for critical items.
    """
    try:
        emergency_service = EmergencyService()
        result = emergency_service.declare_emergency(emergency_type, affected_zones)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error declaring emergency: {str(e)}") 