from fastapi.testclient import TestClient
from app.main import app
from app.models.database import SessionLocal, Item, Container

client = TestClient(app)

def test_search_api():
    """Test the search API endpoint."""
    # First, create a test item and container in the database
    db = SessionLocal()
    
    try:
        # Check if container already exists
        container = db.query(Container).filter(Container.id == "test_container").first()
        if not container:
            container = Container(
                id="test_container",
                zone="Test Zone",
                width=100.0,
                depth=100.0,
                height=100.0
            )
            db.add(container)
        
        # Check if item already exists
        item = db.query(Item).filter(Item.id == "test_item").first()
        if not item:
            item = Item(
                id="test_item",
                name="Test Item",
                width=10.0,
                depth=10.0,
                height=10.0,
                mass=5.0,
                priority=80,
                expiry_date=None,
                usage_limit=10,
                remaining_uses=10,
                preferred_zone="Test Zone",
                is_waste=False,
                container_id="test_container",
                position_width=10.0,
                position_depth=10.0,
                position_height=10.0
            )
            db.add(item)
        
        db.commit()
    finally:
        db.close()
    
    # Test search by ID
    response = client.get("/api/search?itemId=test_item")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == True
    assert result["found"] == True
    assert result["item"]["itemId"] == "test_item"
    assert result["item"]["containerId"] == "test_container"
