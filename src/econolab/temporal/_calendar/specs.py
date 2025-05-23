"""...

...

"""

from dataclasses import dataclass, field
from math import gcd
from typing import Sequence

from .base import EconoCalendar


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
