from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.models.database import get_db, Item, Container
from app.models.schemas import ImportResponse
from app.services.import_export_service import ImportExportService

router = APIRouter()

@router.post("/import/items", response_model=ImportResponse)
async def import_items(file: UploadFile = File(...), auto_place: bool = Form(True), db: Session = Depends(get_db)):
    """
    Import items from a CSV file.
    Optionally auto-place items in available containers.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        import_export_service = ImportExportService()
        items_imported, errors = import_export_service.import_items(file.file)

        # Auto-place items if requested and if there are items to place
        placements = []
        if auto_place and items_imported > 0:
            from app.services.placement_service import PlacementService
            from app.models.schemas import ItemBase, ContainerBase

            # Get all items that don't have a container assigned
            items = db.query(Item).filter(Item.container_id.is_(None)).all()

            # Get all available containers
            containers = db.query(Container).all()

            if items and containers:
                # Convert to schema models
                item_models = [
                    ItemBase(
                        itemId=item.id,
                        name=item.name,
                        width=item.width,
                        depth=item.depth,
                        height=item.height,
                        priority=item.priority,
                        expiryDate=item.expiry_date.isoformat() if item.expiry_date else None,
                        usageLimit=item.usage_limit,
                        preferredZone=item.preferred_zone
                    ) for item in items
                ]

                container_models = [
                    ContainerBase(
                        containerId=container.id,
                        zone=container.zone,
                        width=container.width,
                        depth=container.depth,
                        height=container.height
                    ) for container in containers
                ]

                # Place items
                placement_service = PlacementService()
                placements, _ = placement_service.place_items(item_models, container_models)

        return ImportResponse(
            success=len(errors) == 0,
            itemsImported=items_imported,
            errors=errors,
            placements=placements if 'placements' in locals() else []
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error importing items: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Error importing items: {str(e)}")

@router.post("/import/containers", response_model=ImportResponse)
async def import_containers(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import containers from a CSV file.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        import_export_service = ImportExportService()
        containers_imported, errors = import_export_service.import_containers(file.file)

        return ImportResponse(
            success=len(errors) == 0,
            containersImported=containers_imported,
            errors=errors
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing containers: {str(e)}")

@router.get("/export/arrangement", response_class=PlainTextResponse)
def export_arrangement(db: Session = Depends(get_db)):
    """
    Export the current arrangement to a CSV file.
    """
    try:
        import_export_service = ImportExportService()
        csv_content = import_export_service.export_arrangement()

        return csv_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting arrangement: {str(e)}")
