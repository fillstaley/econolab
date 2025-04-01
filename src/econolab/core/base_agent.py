"""Base class for agents in an EconoLab model."""

from ..temporal import Calendar
from .counters import CounterCollection


class BaseAgent:
    """Base class for agents in an EconoLab model."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.calendar = Calendar(self)
        self.counters = CounterCollection(self)
    
    
    def reset_counters(self) -> None:
        """Resets all of an agent's (transient) counters to 0."""
        for counter in self.counters.transient.values():
            counter.reset()
    
    def act(self) -> None:
        """Perform actions during a model step."""
        raise NotImplementedError
