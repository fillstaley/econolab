"""Base class for agents in an EconoLab model."""

from ..temporal import Calendar
from .counters import Counters


class BaseAgent:
    """Base class for agents in an EconoLab model."""

    def __init__(self, calendar: Calendar, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.calendar = Calendar(self)
        self.counters = Counters()

    def act(self) -> None:
        """Perform actions during a model step."""
        raise NotImplementedError
