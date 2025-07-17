#!/bin/bash

# Dev environnment runs flask off of the built in WSGI server
# Prod environment runs flask off of gunicorn locally
# The live demo runs off of a cloud service using gunicorn

# Check if an environment is provided
if [ -z "$1" ]; then
  echo "Usage: ./run.sh [dev|test|prod]"
  exit 1
fi

ENV=$1

# Set environment-specific variables
if [ "$ENV" == "dev" ]; then
  COMPOSE_FILE="Docker/Dev/compose.yaml"
elif [ "$ENV" == "prod" ]; then
  COMPOSE_FILE="Docker/Prod/compose.yaml"
elif [ "$ENV" == "test" ]; then
  COMPOSE_FILE="Docker/Test/compose.yaml"
else
  echo "Invalid environment: $ENV. Use 'dev' or 'prod'."
  exit 1
fi


# Build and run the application
if [ "$COMPOSE_FILE" == "Docker/Test/compose.yaml" ]; then
  docker-compose -f $COMPOSE_FILE up --build --abort-on-container-exit --exit-code-from test_runner
else
  docker-compose -f $COMPOSE_FILE up --build
fi
