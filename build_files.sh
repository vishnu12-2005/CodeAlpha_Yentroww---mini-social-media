#!/bin/bash
# Run this script during Vercel build to collect static files
set -e

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --run-syncdb
