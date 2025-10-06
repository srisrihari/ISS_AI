import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

def test_identify_waste(client, astronaut_token, test_db):
    """Test identifying waste items."""
    # Create expired and depleted items
    from app.models.database import Item, Container
    
    # Create a container
    container = Container(
        id="waste_container",
        zone="Waste Zone",
        width=100.0,
        depth=100.0,
        height=100.0
    )
    test_db.add(container)
    
    # Create an expired item
    expired_item = Item(
        id="expired_item",
        name="Expired Item",
        width=10.0,
        depth=10.0,
        height=10.0,
        mass=5.0,
        priority=80,
        expiry_date=datetime.utcnow() - timedelta(days=1),  # Expired
        usage_limit=10,
        remaining_uses=10,
        preferred_zone="Waste Zone",
        is_waste=False,
        container_id="waste_container",
        position_width=10.0,
        position_depth=10.0,
        position_height=10.0
    )
    test_db.add(expired_item)
    
    # Create a depleted item
    depleted_item = Item(
        id="depleted_item",
        name="Depleted Item",
        width=10.0,
        depth=10.0,
        height=10.0,
        mass=5.0,
        priority=80,
        expiry_date=datetime.utcnow() + timedelta(days=30),
        usage_limit=10,
        remaining_uses=0,  # Depleted
        preferred_zone="Waste Zone",
        is_waste=False,
        container_id="waste_container",
        position_width=30.0,
        position_depth=30.0,
        position_height=30.0
    )
    test_db.add(depleted_item)
    
    # Create a normal item
    normal_item = Item(
        id="normal_item",
        name="Normal Item",
        width=10.0,
        depth=10.0,
        height=10.0,
        mass=5.0,
        priority=80,
        expiry_date=datetime.utcnow() + timedelta(days=30),
        usage_limit=10,
        remaining_uses=10,
        preferred_zone="Waste Zone",
        is_waste=False,
        container_id="waste_container",
        position_width=50.0,
        position_depth=50.0,
        position_height=50.0
    )
    test_db.add(normal_item)
    
    test_db.commit()
    
    # Test identify waste
    response = client.get(
        "/api/waste/identify",
        headers={"Authorization": f"Bearer {astronaut_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # Should identify both expired and depleted items
    waste_items = response.json()["wasteItems"]
    waste_ids = [item["itemId"] for item in waste_items]
    assert "expired_item" in waste_ids
    assert "depleted_item" in waste_ids
    assert "normal_item" not in waste_ids
    
    # Check if items are marked as waste in the database
    expired_item = test_db.query(Item).filter(Item.id == "expired_item").first()
    depleted_item = test_db.query(Item).filter(Item.id == "depleted_item").first()
    assert expired_item.is_waste == True
    assert depleted_item.is_waste == True

def test_return_plan(client, astronaut_token, test_db):
    """Test creating a return plan for waste items."""
    # Create an undocking container
    from app.models.database import Container
    
    undocking_container = Container(
        id="undocking_container",
        zone="Undocking Zone",
        width=100.0,
        depth=100.0,
        height=100.0
    )
    test_db.add(undocking_container)
    test_db.commit()
    
    # Test create return plan
    response = client.post(
        "/api/waste/return-plan",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "undockingContainerId": "undocking_container",
            "undockingDate": datetime.utcnow().isoformat(),
            "maxWeight": 100.0
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # Check return manifest
    return_manifest = response.json()["returnManifest"]
    assert return_manifest["undockingContainerId"] == "undocking_container"
    
    # Test with non-existent container
    response = client.post(
        "/api/waste/return-plan",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "undockingContainerId": "nonexistent",
            "undockingDate": datetime.utcnow().isoformat(),
            "maxWeight": 100.0
        }
    )
    assert response.status_code == 200  # Still returns success but with empty plan
    assert response.json()["success"] == True
    assert len(response.json()["returnPlan"]) == 0

def test_complete_undocking(client, commander_token, astronaut_token, test_db):
    """Test completing the undocking process."""
    # Create an undocking container with waste items
    from app.models.database import Container, Item
    
    # Create container if it doesn't exist
    undocking_container = test_db.query(Container).filter(Container.id == "undocking_container").first()
    if not undocking_container:
        undocking_container = Container(
            id="undocking_container",
            zone="Undocking Zone",
            width=100.0,
            depth=100.0,
            height=100.0
        )
        test_db.add(undocking_container)
    
    # Create waste items in the undocking container
    waste_item1 = Item(
        id="waste_item1",
        name="Waste Item 1",
        width=10.0,
        depth=10.0,
        height=10.0,
        mass=5.0,
        priority=80,
        expiry_date=datetime.utcnow() - timedelta(days=1),
        usage_limit=10,
        remaining_uses=0,
        preferred_zone="Undocking Zone",
        is_waste=True,
        container_id="undocking_container",
        position_width=10.0,
        position_depth=10.0,
        position_height=10.0
    )
    test_db.add(waste_item1)
    
    waste_item2 = Item(
        id="waste_item2",
        name="Waste Item 2",
        width=10.0,
        depth=10.0,
        height=10.0,
        mass=5.0,
        priority=80,
        expiry_date=datetime.utcnow() - timedelta(days=1),
        usage_limit=10,
        remaining_uses=0,
        preferred_zone="Undocking Zone",
        is_waste=True,
        container_id="undocking_container",
        position_width=30.0,
        position_depth=30.0,
        position_height=30.0
    )
    test_db.add(waste_item2)
    
    test_db.commit()
    
    # Test complete undocking as astronaut (should fail due to permissions)
    response = client.post(
        "/api/waste/complete-undocking",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "undockingContainerId": "undocking_container",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    assert response.status_code == 403  # Forbidden
    
    # Test complete undocking as commander
    response = client.post(
        "/api/waste/complete-undocking",
        headers={"Authorization": f"Bearer {commander_token}"},
        json={
            "undockingContainerId": "undocking_container",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["itemsRemoved"] == 2
    
    # Check if items were removed from the database
    waste_item1 = test_db.query(Item).filter(Item.id == "waste_item1").first()
    waste_item2 = test_db.query(Item).filter(Item.id == "waste_item2").first()
    assert waste_item1 is None
    assert waste_item2 is None
