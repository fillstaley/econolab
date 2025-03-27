"""Base class for agents in an EconoLab model."""

from ..temporal import Calendar
from .counters import Counters


class BaseAgent:
    """Base class for agents in an EconoLab model."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.calendar = Calendar(self)
        self.counters = Counters(self)

    def act(self) -> None:
        """Perform actions during a model step."""
        raise NotImplementedError
