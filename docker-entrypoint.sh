#!/bin/sh
set -e

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
# Django's createsuperuser --noinput uses DJANGO_SUPERUSER_* env vars
if [ -z "$DJANGO_SUPERUSER_USERNAME" ]; then
    # Auto-generate credentials if not provided
    export DJANGO_SUPERUSER_USERNAME="admin"
    export DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
    export DJANGO_SUPERUSER_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")

    echo "============================================"
    echo "Auto-generated superuser credentials:"
    echo "  Username: $DJANGO_SUPERUSER_USERNAME"
    echo "  Password: $DJANGO_SUPERUSER_PASSWORD"
    echo "============================================"
    echo ""
    echo "To set your own credentials, use environment variables:"
    echo "  DJANGO_SUPERUSER_USERNAME"
    echo "  DJANGO_SUPERUSER_PASSWORD"
    echo "  DJANGO_SUPERUSER_EMAIL"
    echo "============================================"
fi

# Create superuser (will silently skip if already exists)
python manage.py createsuperuser --noinput 2>/dev/null || true

# Execute the main command
exec "$@"
