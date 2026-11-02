"""Base contract classes for strictly typed, contract-first communication."""

from __future__ import annotations

__author__ = "Balu Varanasi"
__email__ = "balu@chitram.ai"

import msgspec


class Contract(msgspec.Struct, forbid_unknown_fields=True, kw_only=True):
    """Base contract for all Ojas Ops structured data transfer objects.

    Enforces strict typing, explicit keyword-only construction,
    and automatic rejection of unknown payload fields.
    """


class FrozenContract(msgspec.Struct, frozen=True, forbid_unknown_fields=True, kw_only=True):
    """Base contract for immutable value objects and event records."""


class APIRequest(Contract, forbid_unknown_fields=True, kw_only=True):
    """Base contract for external incoming API requests."""


class APIResponse(Contract, forbid_unknown_fields=True, kw_only=True):
    """Base contract for outgoing API responses."""


class ValueObject(FrozenContract, frozen=True, forbid_unknown_fields=True, kw_only=True):
    """Immutable value object contract (e.g. intervals, time windows)."""


class DomainEventContract(FrozenContract, frozen=True, forbid_unknown_fields=True, kw_only=True):
    """Immutable domain event contract for message brokers and event buses."""
