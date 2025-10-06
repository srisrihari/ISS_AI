#!/bin/bash

# Run all tests with pytest
echo "Running tests..."
cd "$(dirname "$0")"
python -m pytest tests/ -v

# Clean up test database
echo "Cleaning up..."
rm -f test.db

echo "Done!"
