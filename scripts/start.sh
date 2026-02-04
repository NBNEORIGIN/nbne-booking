#!/bin/bash
# Quick start script for NBNE Booking

echo "Starting NBNE Booking (local stack)..."
echo ""

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.local.yml"

if [ ! -f "${COMPOSE_FILE}" ]; then
    echo "Error: ${COMPOSE_FILE} not found. Ensure you are in the project root."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Start containers
echo "Starting containers using docker-compose.local.yml..."
docker compose -f "${COMPOSE_FILE}" up -d

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
        echo "  - Frontend: http://localhost:3000"
        echo "  - API:      http://localhost:8000"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - Mailhog:  http://localhost:8025"
        echo ""
        echo "View logs: docker compose -f ${COMPOSE_FILE} logs -f"
        exit 0
    fi
    sleep 2
done

echo "✗ API health check timed out. Check logs with: docker compose -f ${COMPOSE_FILE} logs"
exit 1
