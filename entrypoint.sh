#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

cd DigitalArchiveServer || exit

if [ ! -f "$SETUP_FILE" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
else
  touch "$SETUP_FILE"
fi

exec "$@"
