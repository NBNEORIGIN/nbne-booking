#!/bin/bash
# Create a new Alembic migration

if [ -z "$1" ]; then
    echo "Usage: ./create_migration.sh 'migration description'"
    exit 1
fi

docker-compose exec api alembic revision --autogenerate -m "$1"
