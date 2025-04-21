"""Base class for an EconoLab model."""

from ..temporal import Calendar
from .counters import CounterCollection


class BaseModel:
    """Base class for all EconoLab models."""
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.calendar = Calendar(self)
        self.counters = CounterCollection(self)
    
    def reset_counters(self) -> None:
        """Resets all of a model's (transient) counters to 0."""
        for counter in self.counters.transient.values():
            counter.reset()
