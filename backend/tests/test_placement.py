import pytest
from fastapi.testclient import TestClient

def test_placement_recommendations(client, astronaut_token):
    """Test placement recommendations."""
    # Test with valid data
    response = client.post(
        "/api/placement",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "items": [
                {
                    "itemId": "test001",
                    "name": "Test Item 1",
                    "width": 10,
                    "depth": 10,
                    "height": 10,
                    "priority": 80,
                    "usageLimit": 10,
                    "preferredZone": "Test Zone"
                },
                {
                    "itemId": "test002",
                    "name": "Test Item 2",
                    "width": 20,
                    "depth": 20,
                    "height": 20,
                    "priority": 90,
                    "usageLimit": 5,
                    "preferredZone": "Another Zone"
                }
            ],
            "containers": [
                {
                    "containerId": "testContA",
                    "zone": "Test Zone",
                    "width": 100,
                    "depth": 100,
                    "height": 100
                },
                {
                    "containerId": "testContB",
                    "zone": "Another Zone",
                    "width": 50,
                    "depth": 50,
                    "height": 50
                }
            ]
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert len(response.json()["placements"]) > 0
    
    # Test with invalid data (negative dimensions)
    response = client.post(
        "/api/placement",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "items": [
                {
                    "itemId": "test003",
                    "name": "Invalid Item",
                    "width": -10,  # Negative width
                    "depth": 10,
                    "height": 10,
                    "priority": 80,
                    "usageLimit": 10,
                    "preferredZone": "Test Zone"
                }
            ],
            "containers": [
                {
                    "containerId": "testContC",
                    "zone": "Test Zone",
                    "width": 100,
                    "depth": 100,
                    "height": 100
                }
            ]
        }
    )
    assert response.status_code == 422  # Validation error
    
    # Test with item too large for container
    response = client.post(
        "/api/placement",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "items": [
                {
                    "itemId": "test004",
                    "name": "Too Large Item",
                    "width": 200,  # Larger than container
                    "depth": 200,
                    "height": 200,
                    "priority": 80,
                    "usageLimit": 10,
                    "preferredZone": "Test Zone"
                }
            ],
            "containers": [
                {
                    "containerId": "testContD",
                    "zone": "Test Zone",
                    "width": 100,
                    "depth": 100,
                    "height": 100
                }
            ]
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert len(response.json()["placements"]) == 0  # No placements possible

def test_advanced_placement(client, astronaut_token):
    """Test advanced placement with rearrangement."""
    # First place some items
    response = client.post(
        "/api/placement",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "items": [
                {
                    "itemId": "lowPriority1",
                    "name": "Low Priority Item 1",
                    "width": 30,
                    "depth": 30,
                    "height": 30,
                    "priority": 20,  # Low priority
                    "usageLimit": 10,
                    "preferredZone": "Test Zone"
                },
                {
                    "itemId": "lowPriority2",
                    "name": "Low Priority Item 2",
                    "width": 30,
                    "depth": 30,
                    "height": 30,
                    "priority": 30,  # Low priority
                    "usageLimit": 10,
                    "preferredZone": "Test Zone"
                }
            ],
            "containers": [
                {
                    "containerId": "rearrangeContA",
                    "zone": "Test Zone",
                    "width": 100,
                    "depth": 100,
                    "height": 100
                },
                {
                    "containerId": "rearrangeContB",
                    "zone": "Another Zone",
                    "width": 100,
                    "depth": 100,
                    "height": 100
                }
            ]
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # Now try to place a high priority item that requires rearrangement
    response = client.post(
        "/api/placement",
        headers={"Authorization": f"Bearer {astronaut_token}"},
        json={
            "items": [
                {
                    "itemId": "highPriority1",
                    "name": "High Priority Item",
                    "width": 80,  # Large item
                    "depth": 80,
                    "height": 80,
                    "priority": 90,  # High priority
                    "usageLimit": 10,
                    "preferredZone": "Test Zone"
                }
            ],
            "containers": [
                {
                    "containerId": "rearrangeContA",
                    "zone": "Test Zone",
                    "width": 100,
                    "depth": 100,
                    "height": 100
                },
                {
                    "containerId": "rearrangeContB",
                    "zone": "Another Zone",
                    "width": 100,
                    "depth": 100,
                    "height": 100
                }
            ]
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    
    # Check if rearrangements were suggested
    result = response.json()
    if len(result["placements"]) > 0:
        # Either the item was placed directly
        assert result["placements"][0]["itemId"] == "highPriority1"
    elif len(result["rearrangements"]) > 0:
        # Or rearrangements were suggested
        assert any(step["itemId"] == "highPriority1" for step in result["rearrangements"])
