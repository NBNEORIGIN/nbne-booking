#!/bin/bash
# Render migration script - runs Alembic migrations on deployment

set -e

echo "🔄 Running database migrations..."
alembic upgrade head

echo "✅ Migrations complete"
