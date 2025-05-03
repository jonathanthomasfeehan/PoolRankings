#!/bin/sh

echo "Fixing permissions for secrets..."

chown appuser:appuser /etc/secrets/poolrankings-firebase-adminsdk-fbsvc-d688c2a06a.json
chmod 400 /etc/secrets/*.json

echo "Starting Gunicorn server..."
exec su appuser -c "gunicorn -w 4 -b 0.0.0.0:5000 app:app"
