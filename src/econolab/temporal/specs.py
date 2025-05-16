"""Specifications for the temporal structure of an EconoLab model.

...

"""

from dataclasses import dataclass, field
from math import gcd
from typing import Sequence


@dataclass(frozen=True, slots=True)
class CalendarSpecification:
    """Defines the temporal structure of an EconoCalendar.
    
    Parameters
    ----------
    minyear : int
        Smallest possible year (must be > 0).
    maxyear : int
        Largest possible year (must be > ``minyear``).
    days_per_week : int
        Number of days in a week (must be > 0).
    days_per_month : int or sequence of int
        If int, number of days in each month (must be > 0).
        If sequence, elements specify days in each month and the length
        specifies ``months_per_year``.
    months_per_year : int, optional
        Number of months in a year (must be > 0). Should be omitted if
        ``days_per_month`` is a sequence (it will be inferred from its length).
    
    Attributes
    ----------
    minyear : int
    maxyear : int
    days_per_week : int
    days_per_month : int or sequence of int
    months_per_year : int
    days_per_year : int
        Total days in a year, summing per-month lengths or uniform months.
    """
    minyear: int = field(default=1)
    maxyear: int = field(default=9_999)
    days_per_week: int = field(default=7)
    days_per_month: int | Sequence[int] = field(default=28)
    months_per_year: int = field(default=12)
    steps_to_days_ratio: tuple[int, int] = field(default=(1, 1))
    
    
    def __post_init__(self):
        for name in ("minyear", "maxyear", "days_per_week"):
            if not isinstance(value := getattr(self, name), int):
                raise TypeError(
                    f"'{name}' must be an int; got type '{type(value).__name__}'"
                )
            if value <= 0:
                raise ValueError(
                    f"'{name}' must be positive; got {value!r}"
                )
        if self.maxyear < self.minyear:
            raise ValueError(
                f"'maxyear' ({self.maxyear}) must be at least equal to "
                f"'minyear' ({self.minyear})"
            )
        
        if isinstance(dpm := self.days_per_month, int):
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
            object.__setattr__(self, 'months_per_year', len(dpm))
        else:
            raise TypeError(
                f"'days_per_month' must be either an int or a Sequence of int; "
                f"got type '{type(dpm).__name__}'"
            )
        
        if not isinstance(self.steps_to_days_ratio, tuple):
            raise TypeError(
                f"'steps_to_days_ratio' must be a tuple of int; "
                f"got type '{type(self.steps_to_days_ratio).__name__}"
            )
        elif length := len(self.steps_to_days_ratio) != 2:
            raise ValueError(
                f"'steps_to_days_ratio' must have length 2; got length {length}"
            )
        for idx, value in enumerate(self.steps_to_days_ratio):
            if not isinstance(value, int):
                raise TypeError(
                    f"'steps_to_days_ratio[{idx}] must be an int; "
                    f"got type '{type(value).__name___}'"
                )
            elif value <= 0:
                raise ValueError(
                    f"'steps_to_days_ratio[{idx}] must be positive; got {value!r}"
                )
        
        # reduce the steps_to_days_ratio if necessary
        steps, days = self.steps_to_days_ratio
        if (divisor := gcd(steps, days)) != 1:
            steps, days = steps // divisor, days // divisor
            object.__setattr__(self, "steps_to_days_ratio", (steps, days))
    
    @property
    def days_per_year(self) -> int:
        """Total days in a year, summing per-month lengths or uniform months."""
        dpm = self.days_per_month
        return sum(dpm) if isinstance(dpm, Sequence) else self.months_per_year * dpm
    
    def to_dict(self) -> dict:
        return {slot: getattr(self, slot) for slot in self.__slots__}
