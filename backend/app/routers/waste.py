from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.schemas import WasteIdentifyResponse, ReturnPlanRequest, ReturnPlanResponse, UndockingRequest, UndockingResponse
from ..services.waste_service import WasteService

router = APIRouter()

@router.get("/waste/identify", response_model=WasteIdentifyResponse)
def identify_waste(db: Session = Depends(get_db)):
    """
    Identify items that are waste (expired or out of uses).
    """
    try:
        waste_service = WasteService()
        waste_items = waste_service.identify_waste()
        
        return WasteIdentifyResponse(
            success=True,
            wasteItems=waste_items
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error identifying waste: {str(e)}")

@router.post("/waste/return-plan", response_model=ReturnPlanResponse)
def create_return_plan(request: ReturnPlanRequest, db: Session = Depends(get_db)):
    """
    Create a plan for returning waste items.
    """
    try:
        waste_service = WasteService()
        return_plan, retrieval_steps, return_manifest = waste_service.create_return_plan(
            request.undockingContainerId,
            request.undockingDate,
            request.maxWeight
        )
        
        return ReturnPlanResponse(
            success=True,
            returnPlan=return_plan,
            retrievalSteps=retrieval_steps,
            returnManifest=return_manifest
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating return plan: {str(e)}")

@router.post("/waste/complete-undocking", response_model=UndockingResponse)
def complete_undocking(request: UndockingRequest, db: Session = Depends(get_db)):
    """
    Complete the undocking process by removing waste items.
    """
    try:
        waste_service = WasteService()
        items_removed = waste_service.complete_undocking(
            request.undockingContainerId,
            request.timestamp
        )
        
        return UndockingResponse(
            success=True,
            itemsRemoved=items_removed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing undocking: {str(e)}")
