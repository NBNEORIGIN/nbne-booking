#!/bin/bash
# Quick start script for NBNE Booking

echo "Starting NBNE Booking..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Start containers
echo "Starting containers..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 5

# Check health
echo ""
echo "Checking API health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ API is healthy!"
        echo ""
        echo "Services running:"
        echo "  - API: http://localhost:8000"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - Health: http://localhost:8000/health"
        echo ""
        echo "View logs: docker-compose logs -f"
        exit 0
    fi
    sleep 2
done

echo "✗ API health check timed out. Check logs with: docker-compose logs"
exit 1
