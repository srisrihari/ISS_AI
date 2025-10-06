from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.models.database import get_db, Item

router = APIRouter()

@router.get("/items", response_model=dict)
def get_items(db: Session = Depends(get_db)):
    """
    Get all items.
    """
    try:
        items = db.query(Item).all()
        # Convert SQLAlchemy models to dictionaries
        item_list = [
            {
                "itemId": item.id,
                "name": item.name,
                "width": item.width,
                "depth": item.depth,
                "height": item.height,
                "mass": item.mass,
                "priority": item.priority,
                "expiryDate": item.expiry_date.isoformat() if item.expiry_date else None,
                "usageLimit": item.usage_limit,
                "remainingUses": item.remaining_uses,
                "preferredZone": item.preferred_zone,
                "isWaste": item.is_waste,
                "containerId": item.container_id
            }
            for item in items
        ]
        return {"items": item_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving items: {str(e)}")

@router.delete("/items/{item_id}")
def remove_item(item_id: str, db: Session = Depends(get_db)):
    """
    Remove an item from its container (but not from the database).
    """
    try:
        # Find the item
        item = db.query(Item).filter(Item.id == item_id).first()

        if not item:
            raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

        # Remove the item from its container
        item.container_id = None
        item.position_width = None
        item.position_depth = None
        item.position_height = None

        # Save changes
        db.commit()

        return {"success": True, "message": f"Item {item_id} removed from container"}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error removing item: {str(e)}")

@router.delete("/items/{item_id}/delete")
def delete_item(item_id: str, db: Session = Depends(get_db)):
    """
    Delete an item completely from the database.
    """
    try:
        # Find the item
        item = db.query(Item).filter(Item.id == item_id).first()

        if not item:
            raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")

        # Delete the item
        db.delete(item)

        # Save changes
        db.commit()

        return {"success": True, "message": f"Item {item_id} deleted from database"}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")
