"""Pytest conftest for sandbox tests."""

import os
import sys
from pathlib import Path

# Ensure sandbox and workspace root are in sys.path
sandbox_dir = Path(__file__).resolve().parent.parent
apps_dir = sandbox_dir.parent
workspace_dir = apps_dir.parent

for path in (workspace_dir, apps_dir, sandbox_dir):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402
from django.core.management import call_command  # noqa: E402

django.setup()
call_command("migrate", verbosity=0)
