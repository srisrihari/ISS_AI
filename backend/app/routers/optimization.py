from fastapi import APIRouter, HTTPException
from typing import List
from ..models.schemas import (
    Container, PlacementItem, RearrangementStep, 
    OptimizationRequest, OptimizationResponse
)
from ..services.batch_optimization_service import BatchOptimizationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
optimization_service = BatchOptimizationService()

@router.post("/optimize-container", response_model=OptimizationResponse)
async def optimize_container(request: OptimizationRequest):
    """
    Optimize the arrangement of items in a container
    """
    try:
        steps, metrics = optimization_service.optimize_container(
            request.container,
            request.items
        )
        
        return OptimizationResponse(
            rearrangementSteps=steps,
            spaceUtilization=metrics.space_utilization,
            accessibilityScore=metrics.accessibility_score,
            stabilityScore=metrics.stability_score,
            priorityDistribution=metrics.priority_distribution,
            movementCount=metrics.movement_count,
            totalDistance=metrics.total_distance
        )
    except Exception as e:
        logger.error(f"Container optimization error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize container: {str(e)}"
        ) 