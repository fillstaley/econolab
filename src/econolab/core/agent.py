"""A base class for all EconoLab agents.

Agents act. They are able to do things that change their state, or the
states of other agents.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from logging import Logger
from typing import cast, Protocol, runtime_checkable, TYPE_CHECKING

from .meta import EconoMeta
from ..temporal import EconoCalendar
from .counters import CounterCollection

if TYPE_CHECKING:
    from ..financial import EconoCurrency


__all__ = ["EconoAgent", "AgentType"]


@runtime_checkable
class EconoModelLike(Protocol):
    logger: Logger
    EconoCalendar: type[EconoCalendar]
    EconoCurrency: type[EconoCurrency]


class AgentType(EconoMeta):
    pass


class EconoAgent(ABC, metaclass=AgentType):
    """Base class for agents in an EconoLab model.
    
    ...
    """
    
    model: EconoModelLike
    unique_id: int

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.calendar = self.model.EconoCalendar(self)
        self.Currency = self.model.EconoCurrency
        self.counters = CounterCollection(self)
    
    
    def reset_counters(self) -> None:
        """Resets all of an agent's (transient) counters to 0."""
        for counter in self.counters.transient.values():
            counter.reset()
    
    def act(self) -> None:
        """Perform actions during a model step."""
        raise NotImplementedError
