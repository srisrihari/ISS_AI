from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_placement_api():
    """Test the placement API endpoint."""
    # Test data
    data = {
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
    
    response = client.post("/api/placement", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == True
    assert len(result["placements"]) > 0
