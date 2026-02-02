#!/bin/bash
# Apply database migrations

docker-compose exec api alembic upgrade head
