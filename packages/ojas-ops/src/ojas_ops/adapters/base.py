"""Domain adapter base protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ojas_ops.scheduling.scheduler import Scheduler


class DomainAdapter(ABC):
    """Abstract adapter that translates industry domain entities into Ojas Ops scheduling models."""

    @abstractmethod
    def build_scheduler(self) -> Scheduler:
        """Construct and configure an Ojas Ops Scheduler for this domain problem."""

