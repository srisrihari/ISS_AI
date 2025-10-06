from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..models.database import get_db
from ..models.schemas import SearchResponse, RetrieveRequest, RetrieveResponse, PlaceRequest, PlaceResponse
from ..services.retrieval_service import RetrievalService

router = APIRouter()

@router.get("/search", response_model=SearchResponse)
def search_item(
    itemId: Optional[str] = Query(None),
    itemName: Optional[str] = Query(None),
    userId: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Search for an item by ID or name.
    """
    if not itemId and not itemName:
        raise HTTPException(status_code=400, detail="Either itemId or itemName must be provided")

    try:
        retrieval_service = RetrievalService()
        found, item, retrieval_steps = retrieval_service.find_item(itemId, itemName)

        return SearchResponse(
            success=True,
            found=found,
            item=item,
            retrievalSteps=retrieval_steps
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching for item: {str(e)}")

@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve_item(request: RetrieveRequest, db: Session = Depends(get_db)):
    """
    Mark an item as retrieved.
    """
    try:
        print(f"Retrieving item: {request.itemId}, User: {request.userId}, Timestamp: {request.timestamp}")
        retrieval_service = RetrievalService()
        success = retrieval_service.retrieve_item(request.itemId, request.userId, request.timestamp)
        print(f"Retrieval success: {success}")

        if not success:
            raise HTTPException(status_code=404, detail="Item not found or could not be retrieved")

        return RetrieveResponse(success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving item: {str(e)}")

@router.post("/place", response_model=PlaceResponse)
def place_item(request: PlaceRequest, db: Session = Depends(get_db)):
    """
    Place an item in a container.
    """
    try:
        retrieval_service = RetrievalService()
        success = retrieval_service.place_item(
            request.itemId,
            request.userId,
            request.timestamp,
            request.containerId,
            request.position
        )

        if not success:
            raise HTTPException(status_code=400, detail="Item could not be placed in the specified position")

        return PlaceResponse(success=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error placing item: {str(e)}")
