"""A class that specifies the temporal structure of an EconoLab model.

...

"""

from __future__ import annotations

from dataclasses import dataclass, field
from logging import Logger
from math import gcd
from typing import NamedTuple, Protocol, runtime_checkable, Sequence, Type

from ..core.meta import EconoMeta
from ._base import EconoDate, EconoDuration


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
    
    __constant_attrs__ = {
        "model",
        "days_per_week",
        "days_per_month_seq",
        "start_year",
        "start_month",
        "start_day",
        "max_year",
        "steps_to_days_ratio"
    }
    __slots__ = ("_agent",)
    
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
    
    
    ####################
    # Class Attributes #
    ####################
    
    model: EconoModel
    days_per_week: int
    days_per_month_seq: Sequence[int]
    start_year: int
    start_month: int
    start_day: int
    max_year: int
    steps_to_days_ratio: StepsDaysRatio
    
    EconoDuration: type[EconoDuration]
    EconoDate: type[EconoDate]
    
    
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
            Sub: Type = type(
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


@dataclass(frozen=True)
class CalendarSpecification:
    """Defines the temporal structure of an EconoCalendar.
    
    ...
    
    Parameters
    ----------
    days_per_week : int, optional
        Number of days in a week (must be > 0), by default 7.
    days_per_month : int or sequence of int, optional
        If int, number of days in each month (must be > 0). If sequence,
        elements specify days in each month and the length specifies
        ``months_per_year``. The default is 28.
    months_per_year : int, optional
        Number of months in a year (must be > 0), by default 12. If
        ``days_per_month`` is a sequence, any provided value will be
        silently ignored.
    start_year : int, optional
        The starting year of the calendar (must be > 0), by default 1.
    start_month : int, optional
        The starting month of the calendar (must be > 0), by default 1.
    start_day : int, optional
        The starting day of the calendar (must be > 0), by default 1.
    max_year : int, optional
        Maximum year (must be greater ``start_year``), by default 9,999.
    steps_to_days: tuple of int, optional
        The ratio of steps to days (must be a pair, and both integers
        must by > 0), by default (1, 1).
    
    Attributes
    ----------
    _days_per_month_seq
    _steps_to_days_ratio
    """
    days_per_week: int = field(default=7)
    days_per_month: int | Sequence[int] = field(default=28)
    months_per_year: int = field(default=12)
    start_year: int = field(default=1)
    start_month: int = field(default = 1)
    start_day: int = field(default=1)
    max_year: int = field(default=9_999)
    steps_to_days: tuple[int, int] = field(default=(1, 1))
    
    _days_per_month_seq: Sequence[int] = field(init=False)
    _steps_to_days_ratio: EconoCalendar.StepsDaysRatio = field(init=False)
    
    
    ###########
    # Methods #
    ###########
    
    def __post_init__(self):
        self._validate_positive_int_fields(
            "days_per_week", "start_year", "start_month", "start_day", "max_year"
        )
        self._validate_and_set_days_per_month_seq()
        self._validate_start_date()
        self._validate_and_set_steps_to_days_ratio()
    
    def to_dict(self) -> dict:
        return {
            "days_per_week": self.days_per_week,
            "days_per_month_seq": self._days_per_month_seq,
            "start_year": self.start_year,
            "start_month": self.start_month,
            "start_day": self.start_day,
            "max_year": self.max_year,
            "steps_to_days_ratio": self._steps_to_days_ratio
        }
    
    
    ##################
    # Helper Methods #
    ##################
    
    def _validate_positive_int_fields(self, *names: str) -> None:
        for name in names:
            value = getattr(self, name)
            if not isinstance(value, int):
                raise TypeError(
                    f"'{name}' must be an int; got type '{type(value).__name__}'"
                )
            elif value <= 0:
                raise ValueError(
                    f"'{name}' must be positive; got {value!r}"
                )
    
    def _validate_positive_int_sequence(self, name: str):
        sequence = getattr(self, name, None)
        if not isinstance(sequence,  Sequence):
            raise TypeError(
                f"'{name}' is not a Sequence; got type '{type(sequence).__name__}'"
            )
        for idx, value in enumerate(sequence):
            if not isinstance(value, int):
                raise TypeError(
                    f"'{name}[{idx}]' must be an int; got type '{type(value).__name__}'"
                )
            if value <= 0:
                raise ValueError(
                    f"'{name}[{idx}]' must be positive; got {value!r}"
                )
    
    def _validate_and_set_days_per_month_seq(self) -> None:
        """Ensures a valid number of days per month, and months per year.
        
        The data is ultimately stored as a sequence of int to be used to
        create a subclass of EconoCalendar.
        """
        dpm = self.days_per_month
        if isinstance(dpm, int):
            self._validate_positive_int_fields("days_per_month", "months_per_year")
            object.__setattr__(self, "_days_per_month_seq", [dpm] * self.months_per_year)
        elif isinstance(dpm, Sequence):
            # note that we silently ignore any provided months_per_year in this case
            self._validate_positive_int_sequence("days_per_month")
            object.__setattr__(self, "_days_per_month_seq", dpm)
            object.__setattr__(self, "months_per_year", len(dpm))
        else:
            raise TypeError(
                f"'days_per_month' must be either an int or a Sequence of int; got type '{type(dpm).__name__}'"
            )
    
    def _validate_start_date(self) -> None:
        """Ensures a valid start date for the calendar.
        
        This method must be called after '_validate_and_set_days_per_month_seq()'.
        """
        if self.start_year > self.max_year:
            raise ValueError(
                f"'start_year' ({self.start_year}) exceeds 'max_year' ({self.max_year})"
            )
        if self.start_month > self.months_per_year:
            raise ValueError(
                f"'start_month' ({self.start_month}) exceeds the number of months ({self.months_per_year})"
            )
        if self.start_day > self._days_per_month_seq[self.start_month-1]:
            raise ValueError(
                f"'start_day' ({self.start_day}) exceeds the number of days in 'start_month' ({self.start_month})"
            )
    
    def _validate_and_set_steps_to_days_ratio(self) -> None:
        """Ensures a valid ratio for converting between steps and days.
        
        The data is ultimately stored as an EconoCalendar.StepsDaysRatio
        instance to be used to create a subclass of EconoCalendar.
        """
        if not isinstance(self.steps_to_days, tuple):
            raise TypeError(
                f"'steps_to_days_ratio' must be a tuple of int; got type '{type(self.steps_to_days).__name__}"
            )
        elif length := len(self.steps_to_days) != 2:
            raise ValueError(
                f"'steps_to_days_ratio' must have length 2; got length {length}"
            )
        self._validate_positive_int_sequence("steps_to_days")
        self._reduce_steps_to_days()
        
        ratio = EconoCalendar.StepsDaysRatio(*self.steps_to_days)
        object.__setattr__(self, "_steps_to_days_ratio", ratio)
    
    def _reduce_steps_to_days(self) -> None:
        steps, days = self.steps_to_days
        if (divisor := gcd(steps, days)) != 1:
            steps, days = steps // divisor, days // divisor
            object.__setattr__(self, "steps_to_days", (steps, days))
