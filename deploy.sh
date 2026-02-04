#!/bin/bash
set -e

echo "🚀 Deploying NBNE Booking Platform to Production"
echo "=================================================="

# Configuration
SERVER_USER="root"
SERVER_HOST="YOUR_SERVER_IP"  # Replace with your server IP
DEPLOY_PATH="/srv/booking"
DOMAIN="booking.nbnesigns.co.uk"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Building Docker image locally...${NC}"
docker compose build api

echo -e "${YELLOW}Step 2: Saving Docker image...${NC}"
docker save 024booking-api:latest | gzip > booking-api.tar.gz

echo -e "${YELLOW}Step 3: Uploading files to server...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} "mkdir -p ${DEPLOY_PATH}"

# Upload application files
scp -r api/ ${SERVER_USER}@${SERVER_HOST}:${DEPLOY_PATH}/
scp -r alembic/ ${SERVER_USER}@${SERVER_HOST}:${DEPLOY_PATH}/
scp -r scripts/ ${SERVER_USER}@${SERVER_HOST}:${DEPLOY_PATH}/
scp Dockerfile ${SERVER_USER}@${SERVER_HOST}:${DEPLOY_PATH}/
scp docker-compose.prod.yml ${SERVER_USER}@${SERVER_HOST}:${DEPLOY_PATH}/docker-compose.yml
scp Caddyfile ${SERVER_USER}@${SERVER_HOST}:${DEPLOY_PATH}/
scp alembic.ini ${SERVER_USER}@${SERVER_HOST}:${DEPLOY_PATH}/
scp .env.production ${SERVER_USER}@${SERVER_HOST}:${DEPLOY_PATH}/.env.example

# Upload Docker image
echo -e "${YELLOW}Step 4: Uploading Docker image...${NC}"
scp booking-api.tar.gz ${SERVER_USER}@${SERVER_HOST}:${DEPLOY_PATH}/

echo -e "${YELLOW}Step 5: Deploying on server...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
cd /srv/booking

# Load Docker image
echo "Loading Docker image..."
docker load < booking-api.tar.gz
rm booking-api.tar.gz

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please create it from .env.example"
    echo "   Edit /srv/booking/.env with your production values"
    exit 1
fi

# Stop existing containers
echo "Stopping existing containers..."
docker compose down || true

# Start new containers
echo "Starting containers..."
docker compose up -d

# Wait for database
echo "Waiting for database..."
sleep 10

# Run migrations
echo "Running database migrations..."
docker compose exec -T api alembic upgrade head

# Show status
echo "Container status:"
docker compose ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Configure DNS: Point booking.nbnesigns.co.uk to this server"
echo "2. Wait for SSL certificate (automatic via Caddy)"
echo "3. Test: https://booking.nbnesigns.co.uk/health"
echo "4. Create admin user via API docs"
ENDSSH

# Cleanup
rm booking-api.tar.gz

echo -e "${GREEN}✅ Deployment script completed!${NC}"
echo ""
echo "Important:"
echo "1. SSH to your server: ssh ${SERVER_USER}@${SERVER_HOST}"
echo "2. Edit .env file: nano /srv/booking/.env"
echo "3. Configure DNS for ${DOMAIN}"
echo "4. Restart containers: cd /srv/booking && docker compose restart"
