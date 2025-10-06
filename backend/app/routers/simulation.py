from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.database import get_db
from ..models.schemas import SimulationRequest, SimulationResponse
from ..services.simulation_service import SimulationService

router = APIRouter()

@router.post("/simulate/day", response_model=SimulationResponse)
def simulate_day(request: SimulationRequest, db: Session = Depends(get_db)):
    """
    Simulate the passage of time.
    """
    try:
        simulation_service = SimulationService()
        new_date, changes = simulation_service.simulate_days(
            request.numOfDays,
            request.toTimestamp,
            request.itemsToBeUsedPerDay
        )
        
        return SimulationResponse(
            success=True,
            newDate=new_date,
            changes=changes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating time: {str(e)}")
