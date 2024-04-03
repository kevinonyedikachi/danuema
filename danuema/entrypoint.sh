#!/bin/sh

# Apply Django migrations
echo "Apply database migrations"
python manage.py migrate

exec "$@"