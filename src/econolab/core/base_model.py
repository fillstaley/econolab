"""Base class for an EconoLab model.

...

"""

import logging
from typing import Optional, Type

from ..temporal import (
    TemporalStructure,
    EconoDate as BaseDate,
    EconoDuration as BaseDuration,
    Calendar as BaseCalendar,
)
from .counters import CounterCollection

class BaseModel:
    """Base class for all EconoLab models.
    
    ...
    
    """
    
    # Model-builders must specify this at class level (or override on instance before init)
    name: str | None = None
    temporal_structure: TemporalStructure | None = None
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self,
        *args,
        name: Optional[str] = None,
        **kwargs
    ) -> None:
        # allow cooperative multiple inheritance
        super().__init__(*args, **kwargs)

        # resolve model name: explicit name arg > attribute > class name
        resolved_name = name or self.name or type(self).__name__
        self.name = resolved_name

        # set up a logger for this model instance
        self.logger = logging.getLogger(f"EconoLab.Model.{self.name}")
        self.logger.debug("Initializing model '%s'", self.name)

        # Use temporal structure from class/instance attribute only
        ts = self.temporal_structure
        if ts is None:
            self.logger.error(
                "No TemporalStructure provided for model '%s' (must set `temporal_structure` on class)",
                self.name
            )
            raise RuntimeError(
                "Models must declare `temporal_structure` as a class attribute before initialization."
            )
        self.temporal_structure = ts
        self.logger.debug(
            "Using TemporalStructure: %s", self.temporal_structure
        )

        # Dynamically create and bind temporal subclasses
        self._bind_temporal_types()
        self.logger.debug("Bound temporal types for model '%s'", self.name)

        # instantiate calendar and counters
        self.calendar = self.Calendar(self)
        self.counters = CounterCollection(self)
        self.logger.debug("Calendar and counters initialized for '%s'", self.name)

    def _bind_temporal_types(self):
        """
        For each base temporal class, create an instance-bound subclass
        that carries both the model reference and its temporal constants.
        """
        for BaseCls in (BaseCalendar, BaseDate, BaseDuration):
            cls_name = f"{self.name}{BaseCls.__name__}"
            Sub: Type = type(
                cls_name,
                (BaseCls,),
                {
                    "_model": self,
                }
            )
            setattr(self, BaseCls.__name__, Sub)
            self.logger.debug("Created temporal subclass %s", cls_name)

    def reset_counters(self) -> None:
        """Resets all of a model's (transient) counters to 0."""
        self.logger.debug(
            "Resetting counters for model '%s'", self.name
        )
        for counter in self.counters.transient.values():
            counter.reset()
            self.logger.debug("Reset counter %s", counter.name)

# --- Usage contract ---
# Model-builders must do:
#
# class MyModel(BaseModel):
#     _temporal_structure = TemporalStructure(
#         days_per_week=7,
#         weeks_per_year=52,
#         months_per_year=12,
#         days_per_month=30,
#     )
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         # now self.Calendar, self.EconoDate, self.EconoDuration exist
#         self.calendar = self.Calendar()
#         ...
