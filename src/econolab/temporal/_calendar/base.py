"""A class that specifies the temporal structure of an EconoLab model.

...

"""

from __future__ import annotations

from logging import Logger
from typing import NamedTuple, Protocol, runtime_checkable, Sequence

from ...core.meta import EconoMeta
from .duration import EconoDuration
from .date import EconoDate


@runtime_checkable
class EconoModel(Protocol):
    steps: int
    logger: Logger


@runtime_checkable
class EconoAgent(Protocol):
    unique_id: int


class EconoCalendar(metaclass=EconoMeta):
    """A class that specifies the temporal structure of an EconoLab model.
    
    ...
    """
    
    class StepsDaysRatio(NamedTuple):
        steps: int
        days: int
        
        def to_days(self, steps: int, /) -> int:
            """Convert a number of steps into a number of days.
            
            Parameters
            ----------
            steps : int
            
            Returns
            -------
            int
                A number of days
            """
            return steps * self.days // self.steps
        
        def to_steps(self, days: int, /) -> int:
            """Convert a number of days into a number of steps.
            
            Parameters
            ----------
            days : int
            
            Returns
            -------
            int
                A number of steps
            """
            return days * self.steps // self.days
    
    
    ##############
    # Attributes #
    ##############
    
    # instance attributes
    __slots__ = ("_agent",)
    
    # class attributes
    EconoDuration: type[EconoDuration]
    EconoDate: type[EconoDate]
    
    # class constants
    __constant_attrs__ = (
        "model",
        "days_per_week",
        "days_per_month_tuple",
        "start_year",
        "start_month",
        "start_day",
        "max_year",
        "steps_to_days_ratio"
    )
    model: EconoModel
    days_per_week: int
    days_per_month_tuple: tuple[int, ...]
    start_year: int
    start_month: int
    start_day: int
    max_year: int
    steps_to_days_ratio: StepsDaysRatio
    
    
    #################
    # Class Methods #
    #################
    
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        
        cls._validate_model_binding()
        cls._validate_calendar_specifications()
        
        cls._bind_temporal_types()
    
    @classmethod
    def new_duration(cls, days: int = 0, *, weeks: int = 0) -> EconoDuration:
        """Create a new EconoDuration object.
        
        This method can be used to create a new EconoDuration object by
        providing the number of days as an integer.
        
        Parameters
        ----------
        days : int, optional
            The number of days, by default 0
        
        Returns
        -------
        EconoDuration
            A new EconoDuration object
        """
        if not (Duration := getattr(cls, "EconoDuration", None)):
            raise AttributeError(
                f"'{cls.__name__}' has no 'EconoDuration' attribute"
            )
        elif not issubclass(Duration, EconoDuration):
            raise TypeError(
                f"'{cls.__name__}.EconoDuration' is not a subclass of 'EconoDuration'"
            )
        return Duration(days, weeks=weeks)
    
    @classmethod
    def new_duration_from_steps(cls, steps: int, /) -> EconoDuration:
        cls._validate_calendar_specifications()
        return cls.new_duration(cls.steps_to_days_ratio.to_days(steps))
    
    @classmethod
    def new_date(cls, year: int, month: int, day: int) -> EconoDate:
        """Create a new EconoDate object.
        
        This method can be used to create a new EconoDate object by providing
        the year, month, and day as integers.
        
        Parameters
        ----------
        year : int
            The year of the date
        month : int
            The month of the date
        day : int
            The day of the date
        
        Returns
        -------
        EconoDate
            A new EconoDate object
        """
        if not (Date := getattr(cls, "EconoDate", None)):
            raise AttributeError(
                f"'{cls.__name__}' has no 'EconoDate' attribute"
            )
        elif not issubclass(Date, EconoDate):
            raise TypeError(
                f"'{cls.__name__}.EconoDate' is not a subclass of 'EconoDate'"
            )
        return Date(year, month, day)
    
    @classmethod
    def new_date_from_steps(cls, steps: int, /) -> EconoDate:
        return cls.start_date() + cls.new_duration_from_steps(steps)
    
    @classmethod
    def start_date(cls) -> EconoDate:
        """Returns the start date of the simulation."""
        cls._validate_calendar_specifications()
        return cls.new_date(cls.start_year, cls.start_month, cls.start_day)
    
    @classmethod
    def today(cls) -> EconoDate:
        """Returns the current date of the simulation."""
        cls._validate_model_binding()
        return cls.new_date_from_steps(cls.model.steps)
    
    @classmethod
    def days_per_month(cls, month: int | None = None) -> int | tuple[int, ...]:
        return cls.days_per_month_tuple[month] if month is not None else cls.days_per_month_tuple
    
    @classmethod
    def days_per_year(cls) -> int:
        return sum(cls.days_per_month_tuple)
    
    
    ##################
    # Helper Methods #
    ##################
    
    @classmethod
    def _validate_model_binding(cls) -> None:
        if not (model := getattr(cls, "model", None)):
            raise AttributeError(f"'{cls.__name__}' has no 'model' attribute")
        elif not isinstance(model, EconoModel):
            raise TypeError(
                f"'{cls.__name__}.model' is not a valid 'EconoModel' object"
            )
    
    # TODO: introduce checks for all "necessary" attributes
    @classmethod
    def _validate_calendar_specifications(cls) -> None:
        pass
    
    @classmethod
    def _bind_temporal_types(cls) -> None:
        for BaseCls in (EconoDuration, EconoDate):
            # choose a name for the subclasses
            cls_name = BaseCls.__name__
            Sub: type = EconoMeta(
                cls_name,
                (BaseCls,),
                {
                    "EconoCalendar": cls,
                }
            )
            # bind to the Calendar with BaseCls.__name__, regardless of cls_name
            setattr(cls, BaseCls.__name__, Sub)
            cls.model.logger.debug("Created temporal subclass %s", cls_name)
    
    
    ###################
    # Special Methods #
    ###################
    
    def __new__(cls, *args, **kwargs) -> EconoCalendar:
        if cls is EconoCalendar:
            raise TypeError(
                "EconoCalendar is an abstract base class; "
                "it cannot be instantiated directly."
            )
        return super().__new__(cls)
    
    def __init__(self, owner: EconoModel | EconoAgent) -> None:
        if not isinstance(owner, EconoModel) and not isinstance(owner, EconoAgent):
            raise TypeError(
                "Calendar 'owner' must be a valid 'EconoModel' or 'EconoAgent' object"
            )
        
        self._agent = owner if isinstance(owner, EconoAgent) else None
        self.model.logger.debug(
            "New calendar created; it belongs to %s",
            f"agent #{self.agent.unique_id}" if self.agent else f"the model {self.model}"
        )
    
    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__}(owner={repr(self.agent or self.model)})>"
        )
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def agent(self) -> EconoAgent | None:
        return self._agent
