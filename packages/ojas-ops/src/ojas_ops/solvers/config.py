"""Solver configuration options for CP-SAT."""

from __future__ import annotations

import msgspec


class SolverConfig(msgspec.Struct, kw_only=True):
    """Configuration parameters for Google OR-Tools CP-SAT solver."""

    time_limit_seconds: float = 30.0
    num_workers: int = 8
    random_seed: int = 42
    log_search_progress: bool = False
    relative_gap_limit: float = 0.0
    stop_after_first_solution: bool = False

