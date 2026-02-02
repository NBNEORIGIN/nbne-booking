#!/bin/bash
# Run tests inside the Docker container

docker-compose exec api pytest "$@"
