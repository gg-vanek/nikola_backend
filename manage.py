#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


# os.environ.setdefault("POSTGRES_DB", "postgres")
# os.environ.setdefault("POSTGRES_USER", "postgres")
# os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
# os.environ.setdefault("POSTGRES_HOST", "localhost")
# os.environ.setdefault("POSTGRES_PORT", "5432")
#
# os.environ.setdefault("BACKEND_HOST", "127.0.0.1")
# os.environ.setdefault("BACKEND_PORT", "8002")
#
# os.environ.setdefault("FRONTEND_HOST", "127.0.0.1")
# os.environ.setdefault("FRONTEND_PORT", "80")
#
# os.environ.setdefault("REDIS_HOST", "localhost")
# os.environ.setdefault("REDIS_PORT", "6379")
#
# os.environ.setdefault("DJANGO_SECRET_KEY", "django-insecure-va=jrmk350#&^7a$gan2&v5#(m8r8$5gp(0dx52g7%8h4cb51p")
# os.environ.setdefault("DEBUG_BACKEND", "true")

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
