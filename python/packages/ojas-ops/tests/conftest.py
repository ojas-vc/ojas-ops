"""Pytest configuration for Ojas Ops."""

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="ojas-ops-test-secret-key",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "file:ojas_ops_test?mode=memory&cache=shared",
                "OPTIONS": {"uri": True},
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django_bolt",
            "ojas_ops",
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    )
    django.setup()
    from django.core.management import call_command

    call_command("migrate", verbosity=0)
