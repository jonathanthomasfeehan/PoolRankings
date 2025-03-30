#!/bin/bash

# filepath: d:\Projects\PoolElo\PoolRankings\run.sh

# Check if an environment is provided
if [ -z "$1" ]; then
  echo "Usage: ./run.sh [dev|prod]"
  exit 1
fi

ENV=$1

# Set environment-specific variables
if [ "$ENV" == "dev" ]; then
  COMPOSE_FILE="Docker/Dev/compose.yaml"
elif [ "$ENV" == "prod" ]; then
  COMPOSE_FILE="Docker/Prod/compose.yaml"
else
  echo "Invalid environment: $ENV. Use 'dev' or 'prod'."
  exit 1
fi


# Build and run the application
docker-compose -f $COMPOSE_FILE up --build