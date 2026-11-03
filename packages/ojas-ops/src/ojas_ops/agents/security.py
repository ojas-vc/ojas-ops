"""Security and runtime credential verification for Ojas Ops agent providers."""

from __future__ import annotations

import os
from pathlib import Path


class MissingAPIKeyError(ValueError):
    """Raised when an agent provider or LLM service is invoked without required credentials."""

    def __init__(self, key_name: str, provider: str, instructions: str = "") -> None:
        self.key_name = key_name
        self.provider = provider
        msg = (
            f"Missing required API key '{key_name}' for provider '{provider}'. "
            f"Please set '{key_name}' in your environment or in the .env file."
        )
        if instructions:
            msg += f" {instructions}"
        super().__init__(msg)


def load_workspace_env(env_path: str | Path | None = None) -> None:
    """Loads environment variables from a .env file into os.environ if not already set."""
    if env_path is not None:
        candidates = [Path(env_path)]
    else:
        current = Path.cwd()
        candidates = [
            current / ".env",
            current.parent / ".env",
            Path("/opt/applications/ojas-vc/ojas-ops/.env"),
            Path("/opt/applications/ojas-vc/ojas/.env"),
        ]

    for candidate in candidates:
        if candidate.is_file():
            try:
                with candidate.open("r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if not stripped or stripped.startswith("#"):
                            continue
                        if "=" in stripped:
                            key, val = stripped.split("=", 1)
                            key = key.strip()
                            val = val.strip().strip("'\"")
                            if key and key not in os.environ:
                                os.environ[key] = val
            except Exception:
                pass
            break


def require_api_key(
    var_name: str,
    provider_name: str,
    instructions: str = "",
) -> str:
    """Verifies that the requested API key is present in environment or .env file.

    Raises MissingAPIKeyError if the key is missing or empty.
    """
    load_workspace_env()
    val = os.getenv(var_name)
    if not val or not val.strip():
        raise MissingAPIKeyError(var_name, provider_name, instructions)
    return val.strip()
