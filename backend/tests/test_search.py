import pytest
from fastapi.testclient import TestClient

def test_search_item(client, astronaut_token, sample_container, sample_item, test_db):
    """Test searching for an item."""
    # First place the item in a container
    from app.models.database import Item
    
    item = test_db.query(Item).filter(Item.id == sample_item.id).first()
    item.container_id = sample_container.id
    item.position_width = 10.0
    item.position_depth = 10.0
    item.position_height = 10.0
    test_db.commit()
    
    # Test search by ID
    response = client.get(
        f"/api/search?itemId={sample_item.id}",
        headers={"Authorization": f"Bearer {astronaut_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["found"] == True
    assert response.json()["item"]["itemId"] == sample_item.id
    assert response.json()["item"]["containerId"] == sample_container.id
    
    # Test search by name
    response = client.get(
        f"/api/search?itemName={sample_item.name}",
        headers={"Authorization": f"Bearer {astronaut_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["found"] == True
    assert response.json()["item"]["itemId"] == sample_item.id
    
    # Test search with non-existent ID
    response = client.get(
        "/api/search?itemId=nonexistent",
        headers={"Authorization": f"Bearer {astronaut_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["found"] == False
    
    # Test search without parameters
    response = client.get(
        "/api/search",
        headers={"Authorization": f"Bearer {astronaut_token}"}
    )
    assert response.status_code == 400  # Bad request

def test_retrieve_item(client, astronaut_token, sample_container, sample_item, test_db):
    """Test retrieving an item."""
    # First place the item in a container
    from app.models.database import Item
    
    item = test_db.query(Item).filter(Item.id == sample_item.id).first()
    item.container_id = sample_container.id
    item.position_width = 10.0
    item.position_depth = 10.0
    item.position_height = 10.0
    item.remaining_uses = 5
    test_db.commit()
    
    # Test retrieve
    response = client.post(
        "/api/retrieve",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "itemId": sample_item.id,
            "userId": "test_user",
            "timestamp": "2023-01-01T12:00:00Z"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # Check if remaining uses decreased
    item = test_db.query(Item).filter(Item.id == sample_item.id).first()
    assert item.remaining_uses == 4
    
    # Test retrieve with non-existent ID
    response = client.post(
        "/api/retrieve",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "itemId": "nonexistent",
            "userId": "test_user",
            "timestamp": "2023-01-01T12:00:00Z"
        }
    )
    assert response.status_code == 404  # Not found

def test_place_item(client, astronaut_token, sample_container, sample_item):
    """Test placing an item."""
    # Test place
    response = client.post(
        "/api/place",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "itemId": sample_item.id,
            "userId": "test_user",
            "timestamp": "2023-01-01T12:00:00Z",
            "containerId": sample_container.id,
            "position": {
                "startCoordinates": {
                    "width": 20.0,
                    "depth": 20.0,
                    "height": 20.0
                },
                "endCoordinates": {
                    "width": 30.0,
                    "depth": 30.0,
                    "height": 30.0
                }
            }
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # Test place with invalid position (outside container)
    response = client.post(
        "/api/place",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "itemId": sample_item.id,
            "userId": "test_user",
            "timestamp": "2023-01-01T12:00:00Z",
            "containerId": sample_container.id,
            "position": {
                "startCoordinates": {
                    "width": 90.0,
                    "depth": 90.0,
                    "height": 90.0
                },
                "endCoordinates": {
                    "width": 110.0,  # Outside container
                    "depth": 110.0,  # Outside container
                    "height": 110.0  # Outside container
                }
            }
        }
    )
    assert response.status_code == 400  # Bad request
