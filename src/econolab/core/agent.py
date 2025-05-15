"""A base class for all EconoLab agents.

Agents act. They are able to do things that change their state, or the
states of other agents.

"""

from __future__ import annotations

from abc import ABC
from typing import Protocol, runtime_checkable, TYPE_CHECKING

from .meta import EconoMeta
from ..temporal import EconoCalendar
from .counters import CounterCollection

if TYPE_CHECKING:
    from .model import EconoModel

# @runtime_checkable
# class EconoModel(Protocol):
#     EconoCalendar: type[EconoCalendar]


class AgentType(EconoMeta):
    pass


class EconoAgent(ABC, metaclass=AgentType):
    """Base class for agents in an EconoLab model.
    
    ...
    
    """

    model: EconoModel
    unique_id: int

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.calendar = self.model.EconoCalendar(self)
        self.counters = CounterCollection(self)
    
    
    def reset_counters(self) -> None:
        """Resets all of an agent's (transient) counters to 0."""
        for counter in self.counters.transient.values():
            counter.reset()
    
    def act(self) -> None:
        """Perform actions during a model step."""
        raise NotImplementedError
