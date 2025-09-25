#!/bin/sh
set -e

# Wait for Postgres to be ready
until pg_isready -h db -p 5432 -U "$POSTGRES_USER"; do
  echo "Waiting for postgres to be up"
  sleep 2
done

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
