"""A base class for all EconoLab models.

Models are universes. That is, they contain everything that is needed
for a simulation.

"""

from logging import getLogger, Logger
from abc import ABC
from re import sub

from .meta import EconoMeta
from .counters import CounterCollection
from ..temporal import (
    EconoCalendar,
    CalendarSpecification,
)
from ..financial import (
    EconoCurrency,
    CurrencyType,
    CurrencySpecification,
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
    EconoCurrency: type[EconoCurrency]
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self,
        *args,
        name: str | None = None,
        calendar_specification: CalendarSpecification | None = None,
        currency_specification: CurrencySpecification | None = None,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        
        resolved_name = name or getattr(self, "name", None) or type(self).__name__
        self.name = self._sanitize_name(resolved_name)
        
        self.logger = getLogger(f"EconoLab.Model.{self.name}")
        self.logger.info("Initializing model '%s'", self.name)

        self.logger.info("Initializing the temporal system....")
        self._init_temporal_system(calendar_specification)

        self.logger.info("Initializing the financial system....")
        self._init_financial_system(currency_specification)
        
        self.logger.info("Initializing the counter system....")
        self._init_counter_system()
    
    
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
    
    def _init_temporal_system(self, specs: CalendarSpecification | None) -> None:
        """Initializes the temporal structure of an EconoModel.
        
        A subclass of `EconoCalendar` is created using the data of a
        `CalendarSpecification` instance (the null-constructor specification
        is used if none is provided), and is bound to a model under the
        attribute `EconoCalendar`.
        
        Parameters
        ----------
        specs : CalendarSpecification
            Dataclass with the needed attributes for subclassing `EconoCalendar`.
        """
        if specs is None:
            specs = CalendarSpecification()
            self.logger.debug(
                "No CalendarSpecification provided; using the default specification."
            )
        elif not isinstance(specs, CalendarSpecification):
            raise TypeError(
                f"'spec' must be an instance of 'CalendarSpecification' if provided; "
                f"got type '{type(specs).__name__}'")
        self.logger.debug(
            "Using CalendarSpecification %s for model %s.",
            specs, self.name
        )
        
        attr = "EconoCalendar"
        Calendar: type = EconoMeta(
            f"{self.name}Calendar",
            (EconoCalendar,), 
            {
                "__qualname__": f"{self.name}.{attr}",
                "model": self,
                **specs.to_dict()
            }
        )
        setattr(self, attr, Calendar)
        self.logger.debug(
            "EconoCalendar subclass %s created for model %s.",
            Calendar.__qualname__, self.name
        )
        
        self.calendar = Calendar(self)
        self.logger.debug(
            "%s instance created for model %s.",
            Calendar.__qualname__, self.name
        )
    
    def _init_financial_system(self, specs: CurrencySpecification | None) -> None:
        """Initializes the financial structure of an EconoModel.
        
        A subclass of `EconoCurrency` is created using the data of a
        `CurrencySpecification` instance (the null-constructor specification
        is used if none is provided), and is bound to a model under the
        attribute `EconoCurrency`.
        
        Parameters
        ----------
        specs : CurrencySpecification
            Dataclass with the needed attributes for subclassing `EconoCurrency`.
        
        Notes
        -----
        EconoModel's only support a single currency per instance.
        """
        if specs is None:
            specs = CurrencySpecification()
            self.logger.debug(
                "No CurrencySpecification provided; using the default specification."
            )
        elif not isinstance(specs, CurrencySpecification):
            raise TypeError(
                f"'spec' must be an instance of 'CurrencySpecification' if provided; "
                f"got type '{type(specs).__name__}'")
        self.logger.debug(
            "Using CurrencySpecification %s for model %s.", specs, self.name
        )
        
        attr = "EconoCurrency"
        Currency = CurrencyType(
            f"{specs.code}Currency",
            (EconoCurrency,), 
            {
                "__qualname__": f"{self.name}.{attr}",
                "model": self,
                **specs.to_dict()
            }
        )
        setattr(self, attr, Currency)
        self.logger.debug(
            "EconoCurrency subclass %s created for model %s",
            Currency.__qualname__, self.name
        )
    
    def _init_counter_system(self) -> None:
        """Initializes the counter system for an EconoModel."""
        self.counters = CounterCollection(self)
        self.logger.debug(
            "CounterCollection instance created for model %s",
            self.name
        )
    
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def _sanitize_name(name: str) -> str:
        return sub(r"\s+", "", name.strip())
