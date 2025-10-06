import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_health():
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("Health check passed!")

def test_placement():
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
                "preferredZone": "Crew Quarters"
            },
            {
                "itemId": "test002",
                "name": "Test Item 2",
                "width": 20,
                "depth": 20,
                "height": 20,
                "priority": 90,
                "usageLimit": 5,
                "preferredZone": "Laboratory"
            }
        ],
        "containers": [
            {
                "containerId": "testContA",
                "zone": "Crew Quarters",
                "width": 100,
                "depth": 100,
                "height": 100
            },
            {
                "containerId": "testContB",
                "zone": "Laboratory",
                "width": 50,
                "depth": 50,
                "height": 50
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/placement", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == True
    assert len(result["placements"]) > 0
    print("Placement test passed!")

def test_search():
    # First, place an item
    test_placement()
    
    # Then search for it
    response = requests.get(f"{BASE_URL}/search?itemId=test001")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == True
    assert result["found"] == True
    assert result["item"]["itemId"] == "test001"
    print("Search test passed!")

def test_waste_identify():
    response = requests.get(f"{BASE_URL}/waste/identify")
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == True
    print("Waste identify test passed!")

def test_simulation():
    data = {
        "numOfDays": 1,
        "itemsToBeUsedPerDay": [
            {
                "itemId": "test001"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/simulate/day", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == True
    assert "newDate" in result
    print("Simulation test passed!")

def run_tests():
    print("Running API tests...")
    
    try:
        test_health()
        test_placement()
        test_search()
        test_waste_identify()
        test_simulation()
        
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {str(e)}")

if __name__ == "__main__":
    # Wait for the server to start
    print("Waiting for server to start...")
    time.sleep(2)
    run_tests()
