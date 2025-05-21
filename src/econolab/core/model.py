"""A base class for all EconoLab models.

Models are universes. That is, they contain everything that is needed
for a simulation.

"""

from logging import getLogger, Logger
from abc import ABC
import re
from typing import Optional, Type

from .meta import EconoMeta
from .counters import CounterCollection
from ..temporal import (
    EconoCalendar,
    CalendarSpecification,
)
from ..financial import (
    CurrencySpecification,
    DEFAULT_CURRENCY_SPECIFICATION,
    EconoCurrency
)


class ModelType(EconoMeta):
    pass


class EconoModel(ABC, metaclass=ModelType):
    """Base class for all EconoLab models.
    
    ...
    
    """
    
    ####################
    # Class Attributes #
    ####################
    
    steps: int
    name: str
    logger: Logger
    
    EconoCalendar: type[EconoCalendar]
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self,
        *args,
        name: Optional[str] = None,
        calendar_specification: CalendarSpecification | None = None,
        currency_specification: CurrencySpecification | None = None,
        **kwargs
    ) -> None:
        # allow cooperative multiple inheritance
        super().__init__(*args, **kwargs)

        # resolve model name: explicit name arg > attribute > class name
        resolved_name = name or getattr(self, "name", None) or type(self).__name__
        self.name = self._sanitize_name(resolved_name)

        # set up a logger for this model instance
        self.logger = getLogger(f"EconoLab.Model.{self.name}")
        self.logger.debug("Initializing model '%s'", self.name)

        # bind a custom subclass of EconoCalendar to the model
        self._init_temporal_system(calendar_specification)

        # bind a custom subclass of EconoCurrency to the model
        # for now, all models are assumed to be single-currency models
        self._bind_currency_type(currency_specification)
        self.logger.debug("Bound monetary types for model '%s'", self.name)
        
        # instantiate calendar and counters
        self.calendar = self.EconoCalendar(self)
        self.counters = CounterCollection(self)
        self.logger.debug("Calendar instance and counters initialized for '%s'", self.name)
    
    
    ###########
    # Methods #
    ###########
    
    def reset_counters(self) -> None:
        """Resets all of a model's (transient) counters to 0."""
        self.logger.debug(
            "Resetting counters for model '%s'", self.name
        )
        for counter in self.counters.transient.values():
            counter.reset()
            self.logger.debug("Reset counter %s", counter.name)
    
    
    ##################
    # Helper Methods #
    ##################
    
    def _init_temporal_system(self, spec: CalendarSpecification | None):
        if spec is None:
            spec = CalendarSpecification()
            self.logger.info(
                "No CalendarSpecification provided for model '%s'; using %s as a default.",
                self.name, spec
            )
        elif isinstance(spec, CalendarSpecification):
            self.logger.debug(
                "Using CalendarSpecification %s for model %s.", spec, self.name
            )
        else:
            raise TypeError(
                f"'spec' must of of type 'CalendarSpecification'; "
                f"got type '{type(spec).__name__}'")
        
        cls_name = "EconoCalendar"
        Sub = type(
            cls_name, (EconoCalendar,), {"model": self, **spec.to_dict()}
        )
        
        attr_name = "EconoCalendar"
        setattr(self, attr_name, Sub)
        self.logger.debug(
            "Created Calendar subclass %s; it is bound to %s.%s",
            cls_name, self.name, attr_name
        )

    def _bind_currency_type(self, specs: CurrencySpecification | None) -> None:
        """Creates a model-bound subclass of the EconoCurrency class.
        
        Uses a `CurrencySpecification` to define a subclass of `EconoCurrency`,
        dynamically named `{CODE}Currency`, where `CODE` is the ISO-style
        currency code from the specification (e.g., 'USD').
        
        The resulting subclass is assigned to the model instance under the
        attribute `EconoCurrency`.
        
        All fields from the specification become class-level attributes on
        the subclass. The `code` field is replaced with a read-only property
        to prevent reassignment and to ensure consistency with the class name.
        
        Parameters
        ----------
        specs : CurrencySpecification
            Dataclass with the needed attributes for subclassing `EconoCurrency`.
        
        See Also
        --------
        econolab.financial.CurrencySpecification :
            Required attributes to subclass `EconoCurrency`.
        _bind_temporal_types : A similar method for binding temporal types.
        
        Notes
        -----
        - Only one currency is supported per model at present.
        - This binding does not attach a back-reference to the model.
        """
        if specs is None:
            specs = DEFAULT_CURRENCY_SPECIFICATION
        elif not isinstance(specs, CurrencySpecification):
            raise TypeError(
                f"'specs' must be a CurrencySpecification instance; "
                f"got {type(specs).__name__}"
            )
        specs_dict = specs.to_dict()
        _code = specs_dict["code"]
        
        # replace code attribute (and possibly others) with a read-only property
        READONLY_ATTRS = {"code"}
        def make_readonly_property(value):
            return property(lambda self: value)
        for attr in READONLY_ATTRS:
            specs_dict[attr] = make_readonly_property(specs_dict[attr])
        
        Sub: Type = type(f"{_code}Currency", (EconoCurrency,), specs_dict)
        setattr(self, EconoCurrency.__name__, Sub)
        self.logger.debug("Created monetary subclass %s", Sub.__name__)
    
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def _sanitize_name(name: str) -> str:
        return re.sub(r"\s+", "", name.strip())
