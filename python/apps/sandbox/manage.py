#!/usr/bin/env python
import os
import sys
from pathlib import Path


def main():
    sandbox_dir = Path(__file__).resolve().parent
    apps_dir = sandbox_dir.parent
    workspace_dir = apps_dir.parent

    for path in (workspace_dir, apps_dir, sandbox_dir):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
