#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Running Space Station Cargo Management System Checker"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if the repository exists
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}Dockerfile not found in current directory.${NC}"
    exit 1
fi

echo "1. Building Docker image..."
docker build -t space-cargo-management .

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker build failed.${NC}"
    exit 1
fi
echo -e "${GREEN}Docker build successful.${NC}"

echo "2. Starting container..."
container_id=$(docker run -d -p 8000:8000 space-cargo-management)

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to start container.${NC}"
    exit 1
fi
echo -e "${GREEN}Container started successfully.${NC}"

# Wait for the application to start
echo "3. Waiting for application to start..."
sleep 10

# Test API endpoints
echo "4. Testing API endpoints..."

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local method=$2
    local expected_status=$3
    
    response=$(curl -s -o /dev/null -w "%{http_code}" -X $method http://localhost:8000/api$endpoint)
    
    if [ "$response" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ $endpoint ($method) - OK${NC}"
        return 0
    else
        echo -e "${RED}✗ $endpoint ($method) - Failed (Expected: $expected_status, Got: $response)${NC}"
        return 1
    fi
}

# Test required endpoints
endpoints=(
    "/placement:POST:200"
    "/search:GET:200"
    "/retrieve:POST:200"
    "/place:POST:200"
    "/waste/identify:GET:200"
    "/waste/return-plan:POST:200"
    "/waste/complete-undocking:POST:200"
    "/simulate/day:POST:200"
    "/import/items:POST:200"
    "/import/containers:POST:200"
    "/export/arrangement:GET:200"
    "/logs:GET:200"
)

failed=0
for endpoint in "${endpoints[@]}"; do
    IFS=':' read -r -a array <<< "$endpoint"
    test_endpoint "${array[0]}" "${array[1]}" "${array[2]}"
    failed=$((failed + $?))
done

# Clean up
echo "5. Cleaning up..."
docker stop $container_id
docker rm $container_id

# Final results
echo "=================================================="
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}$failed tests failed. Please check the output above.${NC}"
    exit 1
fi 