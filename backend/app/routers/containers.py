from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, Container

router = APIRouter()

@router.get("/containers", response_model=dict)
def get_containers(db: Session = Depends(get_db)):
    """
    Get all containers.
    """
    try:
        containers = db.query(Container).all()
        # Convert SQLAlchemy models to dictionaries
        container_list = [
            {
                "containerId": container.id,
                "zone": container.zone,
                "width": container.width,
                "depth": container.depth,
                "height": container.height
            }
            for container in containers
        ]
        return {"containers": container_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving containers: {str(e)}")
