"""Pipeline manifest and ruleset loader for Ojas Ops."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import yaml

from ojas_ops.config import get_ojas_ops_root

logger = logging.getLogger(__name__)


def _pipeline_defs_dir() -> Path:
    return get_ojas_ops_root() / "pipeline_defs"


def _rulesets_dir() -> Path:
    return get_ojas_ops_root() / "rulesets"


def load_pipeline_manifest(pipeline_name: str) -> dict[str, Any]:
    """Load and parse a pipeline manifest YAML file."""
    path = _pipeline_defs_dir() / f"{pipeline_name}.yaml"
    if not path.is_file():
        # Try with direct name if user passed with extension
        if pipeline_name.endswith((".yaml", ".yml")):
            path = _pipeline_defs_dir() / pipeline_name
    if not path.is_file():
        available = [p.stem for p in _pipeline_defs_dir().glob("*.yaml")]
        raise FileNotFoundError(
            f"Pipeline manifest '{pipeline_name}' not found at {path}. Available: {available}"
        )

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Pipeline manifest at {path} did not parse into a dictionary.")
    return data


def load_ruleset(ruleset_name: str) -> dict[str, Any]:
    """Load and parse an operational ruleset policy YAML file."""
    path = _rulesets_dir() / f"{ruleset_name}.yaml"
    if not path.is_file() and ruleset_name.endswith((".yaml", ".yml")):
        path = _rulesets_dir() / ruleset_name
    if not path.is_file():
        available = [r.stem for r in _rulesets_dir().glob("*.yaml")]
        raise FileNotFoundError(
            f"Ruleset policy '{ruleset_name}' not found at {path}. Available: {available}"
        )

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Ruleset at {path} did not parse into a dictionary.")
    return data


def list_available_pipelines() -> list[dict[str, Any]]:
    """Scan and list all installed pipeline manifests with metadata."""
    defs_dir = _pipeline_defs_dir()
    if not defs_dir.exists():
        return []

    manifests = []
    for f in sorted(defs_dir.glob("*.yaml")):
        try:
            with open(f, encoding="utf-8") as yf:
                doc = yaml.safe_load(yf)
            if isinstance(doc, dict) and "name" in doc:
                manifests.append({
                    "name": doc.get("name", f.stem),
                    "version": str(doc.get("version", "1.0")),
                    "description": doc.get("description", "").strip(),
                    "category": doc.get("category", "custom"),
                    "stability": doc.get("stability", "production"),
                    "stages_count": len(doc.get("stages", [])),
                    "compatible_rulesets": doc.get("compatible_rulesets", []),
                })
        except Exception as e:
            logger.warning("Failed to parse pipeline manifest %s: %s", f, e)
    return manifests


def list_available_rulesets() -> list[dict[str, Any]]:
    """Scan and list all installed ruleset policies with metadata."""
    r_dir = _rulesets_dir()
    if not r_dir.exists():
        return []

    rulesets = []
    for f in sorted(r_dir.glob("*.yaml")):
        try:
            with open(f, encoding="utf-8") as yf:
                doc = yaml.safe_load(yf)
            if isinstance(doc, dict) and "name" in doc:
                rulesets.append({
                    "name": doc.get("name", f.stem),
                    "version": str(doc.get("version", "1.0")),
                    "domain": doc.get("domain", "general"),
                    "description": doc.get("description", "").strip(),
                })
        except Exception as e:
            logger.warning("Failed to parse ruleset policy %s: %s", f, e)
    return rulesets

