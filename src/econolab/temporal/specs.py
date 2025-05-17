"""Specifications for the temporal structure of an EconoLab model.

...

"""

from dataclasses import dataclass, field
from math import gcd
from typing import Sequence

from .calendar_new import EconoCalendar


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
    
    
    def __post_init__(self):
        self._validate_int_fields(
            "days_per_week", "start_year", "start_month", "start_day", "max_year"
        )
        self._validate_days_per_month_seq()
        self._set_days_per_month_seq()
        
        self._validate_start_date()
        
        self._validate_steps_to_days_ratio()
        self._set_steps_to_days_ratio()
    
    
    ##################
    # Helper Methods #
    ##################
    
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
    
    def _validate_int_fields(self, *names: str) -> None:
        for name in names:
            if not isinstance(value := getattr(self, name), int):
                raise TypeError(
                    f"'{name}' must be an int; got type '{type(value).__name__}'"
                )
            if value <= 0:
                raise ValueError(
                    f"'{name}' must be positive; got {value!r}"
                )
    
    def _validate_days_per_month_seq(self) -> None:
        dpm = self.days_per_month
        if isinstance(dpm, int):
            # verify that months_per_year is an int and both are positive
            if not isinstance(self.months_per_year, int):
                raise TypeError(
                    f"'months_per_year' must be an int; "
                    f"got type '{type(self.months_per_year)}'"
                )
            for name in ("days_per_month", "months_per_year"):
                if (value := getattr(self, name)) <= 0:
                    raise ValueError(
                        f"'{name}' must be positive; got {value!r}"
                    )
        elif isinstance(dpm, Sequence):
            # verify each element is an int and infer months_per_year
            # note that we silently ignore any provided months_per_year
            for month, days in enumerate(dpm):
                if not isinstance(days, int):
                    raise TypeError(
                        f"'days_per_month[{month}]' must be an int; "
                        f"got type '{type(days).__name__}'"
                    )
                if days <= 0:
                    raise ValueError(
                        f"days_per_month[{month}] must be positive; got {days!r}"
                    )
        else:
            raise TypeError(
                f"'days_per_month' must be either an int or a Sequence of int; "
                f"got type '{type(dpm).__name__}'"
            )
    
    def _set_days_per_month_seq(self) -> None:
        dpm = self.days_per_month
        if isinstance(dpm, int):
            object.__setattr__(self, "days_per_month", [dpm] * self.months_per_year)
        else: # is Sequence of int
            object.__setattr__(self, 'months_per_year', len(dpm))
        object.__setattr__(self, "_days_per_month_seq", self.days_per_month)
    
    def _validate_start_date(self) -> None:
        if self.start_year > self.max_year:
            raise ValueError(
                f"'start_year' ({self.start_year}) exceeds "
                f"'max_year' ({self.max_year})"
            )
        if self.start_month > self.months_per_year:
            raise ValueError(
                f"'start_month' ({self.start_month}) exceeds "
                f"the number of months ({self.months_per_year})"
            )
        if self.start_day > self._days_per_month_seq[self.start_month-1]:
            raise ValueError(
                f"'start_day' ({self.start_day}) exceeds "
                f"the number of days in 'start_month' ({self.start_month})"
            )
    
    def _validate_steps_to_days_ratio(self) -> None:
        if not isinstance(self.steps_to_days, tuple):
            raise TypeError(
                f"'steps_to_days_ratio' must be a tuple of int; "
                f"got type '{type(self.steps_to_days).__name__}"
            )
        elif length := len(self.steps_to_days) != 2:
            raise ValueError(
                f"'steps_to_days_ratio' must have length 2; got length {length}"
            )
        for idx, value in enumerate(self.steps_to_days):
            if not isinstance(value, int):
                raise TypeError(
                    f"'steps_to_days_ratio[{idx}] must be an int; "
                    f"got type '{type(value).__name___}'"
                )
            elif value <= 0:
                raise ValueError(
                    f"'steps_to_days_ratio[{idx}] must be positive; got {value!r}"
                )
    
    def _set_steps_to_days_ratio(self) -> None:
        steps, days = self.steps_to_days
        if (divisor := gcd(steps, days)) != 1:
            steps, days = steps // divisor, days // divisor
            object.__setattr__(self, "steps_to_days", (steps, days))
        ratio = EconoCalendar.StepsDaysRatio(*self.steps_to_days)
        object.__setattr__(self, "_steps_to_days_ratio", ratio)
