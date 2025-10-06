from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..models.database import get_db
from ..models.schemas import PlacementRequest, PlacementResponse
from ..services.placement_service import PlacementService

router = APIRouter()

@router.post("/placement", response_model=PlacementResponse)
def placement_recommendations(request: PlacementRequest, db: Session = Depends(get_db)):
    """
    Get placement recommendations for items.
    """
    try:
        placement_service = PlacementService()
        placements, rearrangements = placement_service.place_items(request.items, request.containers)
        
        return PlacementResponse(
            success=True,
            placements=placements,
            rearrangements=rearrangements
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing placement request: {str(e)}")
