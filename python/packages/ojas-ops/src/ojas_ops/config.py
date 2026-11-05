"""Runtime configuration and environment loader for Ojas Ops."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def _load_dotenv_file(filepath: Path) -> None:
    """Parse key=value pairs from a .env file into os.environ if not already set."""
    if not filepath.is_file():
        return
    import re

    with open(filepath, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip()
            if val[:1] in ("'", '"'):
                quote = val[0]
                end = val.find(quote, 1)
                val = val[1:end] if end != -1 else val[1:]
            else:
                match = re.search(r"(^|\s)#", val)
                if match:
                    val = val[: match.start()]
                val = val.strip()
            if key and key not in os.environ:
                os.environ[key] = val


def load_env() -> None:
    """Discovers and loads .env files across project root, package root, and parent workspaces."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parents[4] / ".env",  # ojas-ops root
        Path(__file__).resolve().parents[5] / "ojas" / "python" / ".env",  # sibling ojas/python/.env
        Path(__file__).resolve().parents[5] / ".env",  # ojas-vc root
    ]
    for c in candidates:
        if c.exists():
            _load_dotenv_file(c)


# Auto-load on import
load_env()


def get_anthropic_api_key() -> Optional[str]:
    """Retrieve ANTHROPIC_API_KEY from environment."""
    return os.getenv("ANTHROPIC_API_KEY")


def get_temporal_host() -> str:
    """Retrieve TEMPORAL_HOST from environment, defaulting to localhost:7233."""
    return os.getenv("TEMPORAL_HOST", "localhost:7233")


def get_ojas_ops_root() -> Path:
    """Retrieve root directory of ojas-ops repository."""
    env_root = os.getenv("OJAS_OPS_ROOT")
    if env_root:
        return Path(env_root)
    # Default to 4 levels up from this file: python/packages/ojas-ops/src/ojas_ops/config.py -> ojas-ops
    return Path(__file__).resolve().parents[4]


def get_projects_dir() -> Path:
    """Retrieve directory for local project workspaces."""
    return get_ojas_ops_root() / "projects"

