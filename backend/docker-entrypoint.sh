#!/bin/sh
set -e

should_bootstrap=0
for arg in "$@"; do
  case "$arg" in
    runserver|gunicorn)
      should_bootstrap=1
      ;;
  esac
done

if [ "$should_bootstrap" -eq 1 ]; then
  python manage.py migrate --noinput
  python manage.py seed_demo
fi

exec "$@"
