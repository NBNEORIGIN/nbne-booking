#!/bin/bash
# NBNE Booking - VPS Setup Script
# Run this on the VPS to prepare the deployment environment

set -e

echo "=========================================="
echo "NBNE Booking - VPS Setup"
echo "=========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "❌ Do not run as root. Run as user 'toby' with sudo access."
   exit 1
fi

# Variables
DEPLOY_DIR="/srv/booking"
REPO_URL="https://github.com/NBNEORIGIN/nbne-booking.git"
NETWORK_NAME="nbne-network"
POSTGRES_CONTAINER="nbne-postgres"

echo ""
echo "📋 Pre-flight checks..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi
echo "✅ Docker installed"

# Check Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose plugin."
    exit 1
fi
echo "✅ Docker Compose installed"

# Check Caddy
if ! command -v caddy &> /dev/null; then
    echo "❌ Caddy not found. Please install Caddy first."
    exit 1
fi
echo "✅ Caddy installed"

# Check if Postgres container exists
if ! docker ps -a --format '{{.Names}}' | grep -q "^${POSTGRES_CONTAINER}$"; then
    echo "❌ Postgres container '${POSTGRES_CONTAINER}' not found."
    echo "   Please ensure nbne-postgres is running."
    exit 1
fi
echo "✅ Postgres container exists"

# Check if network exists
if ! docker network ls --format '{{.Name}}' | grep -q "^${NETWORK_NAME}$"; then
    echo "⚠️  Network '${NETWORK_NAME}' not found. Creating..."
    docker network create ${NETWORK_NAME}
    echo "✅ Network created"
else
    echo "✅ Network exists"
fi

# Ensure Postgres is on the network
if ! docker network inspect ${NETWORK_NAME} --format '{{range .Containers}}{{.Name}} {{end}}' | grep -q "${POSTGRES_CONTAINER}"; then
    echo "⚠️  Connecting ${POSTGRES_CONTAINER} to ${NETWORK_NAME}..."
    docker network connect ${NETWORK_NAME} ${POSTGRES_CONTAINER} || echo "   (Already connected or error - continuing...)"
fi
echo "✅ Postgres connected to network"

echo ""
echo "📁 Setting up deployment directory..."

# Create deployment directory
if [ ! -d "$DEPLOY_DIR" ]; then
    sudo mkdir -p "$DEPLOY_DIR"
    sudo chown toby:toby "$DEPLOY_DIR"
    echo "✅ Created $DEPLOY_DIR"
else
    echo "✅ Directory exists"
fi

cd "$DEPLOY_DIR"

# Clone or update repository
if [ ! -d "$DEPLOY_DIR/app" ]; then
    echo "📥 Cloning repository..."
    git clone "$REPO_URL" app
    echo "✅ Repository cloned"
else
    echo "📥 Updating repository..."
    cd app
    git pull
    cd ..
    echo "✅ Repository updated"
fi

# Create docker directory
mkdir -p docker
mkdir -p docs

# Copy docker-compose file
if [ -f "$DEPLOY_DIR/app/docker-compose.vps.yml" ]; then
    cp "$DEPLOY_DIR/app/docker-compose.vps.yml" "$DEPLOY_DIR/docker/docker-compose.yml"
    echo "✅ Docker Compose file copied"
else
    echo "❌ docker-compose.vps.yml not found in repository"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    if [ -f "$DEPLOY_DIR/app/.env.vps.example" ]; then
        cp "$DEPLOY_DIR/app/.env.vps.example" "$DEPLOY_DIR/.env"
        echo "⚠️  Created .env from example - YOU MUST EDIT THIS FILE"
        echo "   Edit: $DEPLOY_DIR/.env"
    else
        echo "❌ .env.vps.example not found in repository"
        exit 1
    fi
else
    echo "✅ .env file exists"
fi

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo "1. Edit environment variables:"
echo "   nano $DEPLOY_DIR/.env"
echo ""
echo "2. Build and start the application:"
echo "   cd $DEPLOY_DIR/docker"
echo "   docker compose up -d --build"
echo ""
echo "3. Run database migrations:"
echo "   docker exec booking-app alembic upgrade head"
echo ""
echo "4. Check logs:"
echo "   docker logs -f booking-app"
echo ""
echo "5. Test health endpoint:"
echo "   curl http://localhost:8000/health"
echo ""
