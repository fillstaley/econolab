"""...

...

"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import total_ordering
from typing import Sequence, Protocol, runtime_checkable

from numpy import floor

from .temporal_structure import TemporalStructure


@runtime_checkable
class EconoModel(Protocol):
    temporal_structure: TemporalStructure


@total_ordering
class EconoDuration:
    """A duration of EconoLab time, measured in days.
    
    Parameters
    ----------
    days : int
        The number of days in the duration, default is 0
    weeks : int
        The additional number of weeks in the duration, default is 0
    
    Attributes
    ----------
    days : int
        The number of days in the duration
    
    Examples
    --------
    >>> duration = EconoDuration(7)
    >>> duration
    EconoDuration(7)
    >>> print(duration)
    7 days
    >>> duration.days
    7
    >>> duration + EconoDuration(10)
    EconoDuration(17)
    >>> duration - EconoDuration(3)
    EconoDuration(4)
    >>> duration * 2
    EconoDuration(14)
    >>> duration / 2
    EconoDuration(3)
    >>> duration // 2
    EconoDuration(3)
    >>> duration // EconoDuration(3)
    EconoDuration(2)
    >>> duration % EconoDuration(3)
    EconoDuration(1)
    >>> divmod(duration, EconoDuration(3))
    (EconoDuration(2), EconoDuration(1))
    >>> -duration
    EconoDuration(-7)
    >>> abs(duration)
    EconoDuration(7)
    >>> abs(-duration)
    EconoDuration(7)
    """
    
    _model: EconoModel | None = None
    __slots__ = ("_days",)
    
    
    ###################
    # Special Methods #
    ###################
    
    def __eq__(self, other: EconoDuration) -> bool:
        if isinstance(other, type(self)):
            return self.days == other.days
        return NotImplemented

    def __lt__(self, other: EconoDuration) -> bool:
        if isinstance(other, type(self)):
            return self.days < other.days
        return NotImplemented
    
    def __bool__(self) -> bool:
        return bool(self.days)

    def __add__(self, other: EconoDuration) -> EconoDuration:
        if isinstance(other, type(self)):
            return type(self)(self.days + other.days)
        return NotImplemented

    def __sub__(self, other: EconoDuration) -> EconoDuration:
        if isinstance(other, type(self)):
            return type(self)(self.days - other.days)
        return NotImplemented
    
    def __mul__(self, other: int | float) -> EconoDuration:
        if isinstance(other, int | float):
            return type(self)(self.days * other)
        return NotImplemented
    
    __rmul__ = __mul__
    
    def __truediv__(self, other: EconoDuration | int | float) -> float | EconoDuration:
        if isinstance(other, type(self)):
            return self.days / other.days
        elif isinstance(other, int | float):
            return type(self)(self.days / other)
        return NotImplemented
    
    def __floordiv__(self, other: EconoDuration | int) -> int | EconoDuration:
        if isinstance(other, type(self)):
            return self.days // other.days
        elif isinstance(other, int):
            return type(self)(self.days // other)
        return NotImplemented
    
    def __mod__(self, other: EconoDuration) -> EconoDuration:
        if isinstance(other, type(self)):
            return type(self)(self.days % other.days)
        return NotImplemented
    
    def __divmod__(self, other: EconoDuration) -> tuple[int, EconoDuration]:
        if isinstance(other, type(self)):
            return self // other, self % other
        return NotImplemented
    
    def __neg__(self) -> EconoDuration:
        return type(self)(-self.days)
    
    def __pos__(self) -> EconoDuration:
        return self
    
    def __abs__(self) -> EconoDuration:
        return type(self)(abs(self.days))
    
    def __hash__(self):
        return hash(self._days)
    
    def __init__(self, days: int | float = 0, weeks: int | float = 0):
        self._days = int(
            floor(days + weeks * self._model.temporal_structure.days_per_week)
        )

    def __repr__(self):
        return f"{type(self).__name__}(days={self.days})"
    
    def __str__(self) -> str:
        return "1 day" if self.days == 1 else f"{self.days} days"
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def days(self) -> int:
        """The number of days in the duration."""
        return self._days
    
    @days.setter
    def days(self, value: int) -> None:
        raise AttributeError("readonly attribute")


@total_ordering
class EconoDate:
    """
    A point in EconoLab time represented as a discrete calendar date.

    An EconoDate object encapsulates a specific moment in the simulation's calendar,
    defined by a year, month, and day. The date is based on a fixed temporal structure,
    with a set number of days per month and months per year (imported from the configuration).
    EconoDate objects are immutable; once created, their year, month, and day cannot be changed.

    Parameters
    ----------
    year : int
        The year component of the date. Must be between MINYEAR and MAXYEAR.
    month : int
        The month component of the date. Must be between 1 and MONTHS_PER_YEAR.
    day : int
        The day component of the date. Must be between 1 and DAYS_PER_MONTH.

    Attributes
    ----------
    year : int
        The year of the date.
    month : int
        The month of the date.
    day : int
        The day of the date.

    Methods
    -------
    to_days() -> int
        Convert the EconoDate to an integer count of days elapsed since the base year
        (MINYEAR), according to the configured temporal structure.
    replace(year: int = None, month: int = None, day: int = None) -> EconoDate
        Return a new EconoDate with any specified components replaced by new values.
    weekday() -> int
        Return the day of the week (to be implemented).
    
    Operator Overloads
    ------------------
    __eq__(other: EconoDate) -> bool
        Compare two EconoDate objects for equality based on (year, month, day).
    __lt__(other: EconoDate) -> bool
        Compare two EconoDate objects lexicographically.
    __add__(other: EconoDuration) -> EconoDate
        Return a new EconoDate by adding a duration (in days) to the current date.
    __sub__(other: EconoDuration | EconoDate) -> EconoDate | EconoDuration
        Subtract a duration from a date (yielding a new date) or subtract two dates
        (yielding a duration).

    Examples
    --------
    >>> d1 = EconoDate(2021, 1, 1)
    >>> d1
    EconoDate(2021, 1, 1)
    >>> d1.to_days()  
    <number of days from MINYEAR to January 1, 2021>
    >>> d2 = d1.replace(month=2)
    >>> d2
    EconoDate(2021, 2, 1)

    Note
    ----
    EconoDate objects are immutable. Attempting to set attributes (e.g., d1.year = 2020)
    will raise an AttributeError.
    
    """
    
    _model: EconoModel | None = None
    __slots__ = ("_year", "_month", "_day")
    
    #################
    # Class Methods #
    #################
    
    @classmethod
    def from_days(cls, days: int) -> EconoDate:
        """
        Create an EconoDate object from a given number of days elapsed since MINYEAR.

        This method converts a number of days into a discrete calendar date, assuming a
        fixed calendar with DAYS_PER_MONTH days per month and MONTHS_PER_YEAR months per
        year, starting at MINYEAR. If the computed year exceeds MAXYEAR, a ValueError is
        raised.

        Parameters
        ----------
        days : int
            The number of days elapsed since the beginning of the calendar (MINYEAR).

        Returns
        -------
        EconoDate
            A new EconoDate object corresponding to the given number of days.

        Raises
        ------
        ValueError
            If the calculated year exceeds MAXYEAR.
        
        """
        if cls._model is None:
            raise RuntimeError(f"{cls} is not bound to a model.")
        
        if not isinstance(days, int) or days < 1:
            raise ValueError("'days' must be an integer and at least 1")
        
        ts = cls._model.temporal_structure
        
        def _divmod(n: int, d: int | Sequence[int]) -> tuple[int, int]:
            if isinstance(d, int):
                return divmod(n, d)
            for i, days_in_month in enumerate(d):
                if n < days_in_month:
                    return i, n
                n -= days_in_month
            raise ValueError("Value exceeds total days in a year")

        year_offset, day_of_year = _divmod(days - 1, ts.days_per_year)
        month_offset, day_offset = _divmod(day_of_year, ts.days_per_month)
        
        if (year := ts.minyear + year_offset) > ts.maxyear:
            raise ValueError(f"Too many days: {days} exceeds maximum number of years ({ts.maxyear})")
        month = 1 + month_offset
        day = 1 + day_offset
        return cls(year, month, day)
    
    @classmethod
    def min(cls) -> EconoDate:
        return cls(year=cls._model.temporal_structure.minyear, month=1, day=1)
    
    @classmethod
    def max(cls) -> EconoDate:
        ts = cls._model.temporal_structure
        last_day = (
            ts.days_per_month[-1] if isinstance(ts.days_per_month, Sequence) else
            ts.days_per_month
        )
        return cls(ts.maxyear, ts.months_per_year, last_day)
    
    
    ###################
    # Special Methods #
    ###################

    def __eq__(self, other: EconoDate) -> bool:
        if isinstance(other, type(self)):
            return (self.year, self.month, self.day) == (other.year, other.month, other.day)
        return NotImplemented

    def __lt__(self, other: EconoDate) -> bool:
        if isinstance(other, type(self)):
            return (self.year, self.month, self.day) < (other.year, other.month, other.day)
        return NotImplemented
    
    def __add__(self, other: EconoDuration) -> EconoDate:
        if isinstance(other, EconoDuration) and self._model is other._model:
            return type(self).from_days(self.to_days() + other.days)
        return NotImplemented
    
    __radd__ = __add__
    
    def __sub__(self, other: EconoDuration | EconoDate) -> EconoDate | EconoDuration:
        if isinstance(other, EconoDuration) and self._model is other._model:
            return type(self).from_days(self.to_days() - other.days)
        elif isinstance(other, type(self)):
            return self._model.EconoDuration(self.to_days() - other.to_days())
        return NotImplemented
    
    __rsub__ = __sub__
    
    def __init__(self, year: int, month: int, day: int):
        if self._model is None:
            raise RuntimeError(f"{type(self)} is not bound to a model.")

        ts = self._model.temporal_structure

        if not ts.minyear <= year <= ts.maxyear:
            raise ValueError(f"year must be between {ts.minyear} and {ts.maxyear}")
        if not 1 <= month <= ts.months_per_year:
            raise ValueError(f"month must be between 1 and {ts.months_per_year}")
        max_day = (
            ts.days_per_month[month - 1] if isinstance(ts.days_per_month, Sequence) else
            ts.days_per_month
        )
        if not 1 <= day <= max_day:
            raise ValueError(f"day must be between 1 and {max_day}")

        self._year = year
        self._month = month
        self._day = day
    
    def __repr__(self):
        return f"EconoDate({self.year}, {self.month}, {self.day})"
    
    def __str__(self):
        return f"{self.year}-{self.month}-{self.day}"
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def year(self) -> int:
        """The year of the date."""
        return self._year
    
    @year.setter
    def year(self, value: int) -> None:
        raise AttributeError("readonly attribute")
    
    @property
    def month(self) -> int:
        """The month of the date."""
        return self._month
    
    @month.setter
    def month(self, value: int) -> None:
        raise AttributeError("readonly attribute")
    
    @property
    def day(self) -> int:
        """The day of the date."""
        return self._day
    
    @day.setter
    def day(self, value: int) -> None:
        raise AttributeError("readonly attribute")
    
    
    ###########
    # Methods #
    ###########
    
    def to_days(self) -> int:
        """
        Convert an EconoDate to an ordinal number of days.

        The conversion is computed using the formula:
        
            total_days = (year - MINYEAR) * (MONTHS_PER_YEAR * DAYS_PER_MONTH)
                            + (month - 1) * DAYS_PER_MONTH
                            + day

        Thus, EconoDate(MINYEAR, 1, 1) is mapped to day 1. This calculation assumes
        that the calendar is fixed with a constant number of days per month and months
        per year, as defined by the global configuration values.

        Returns
        -------
        int
            An ordinal number of days relative to EconoDate(MINYEAR, 1, 1) as day 1

        Examples
        --------
        >>> d = EconoDate(2021, 1, 1)
        >>> d.to_days()
        360 * (2021 - MINYEAR)
        
        """
        ts = self._model.temporal_structure
        days  = self.day
        days += (
            sum(ts.days_per_month[:self.month - 1])
            if isinstance(ts.days_per_month, Sequence)
            else (self.month - 1) * ts.days_per_month
        )
        days += (self.year - ts.minyear) * ts.days_per_year
        return days
    
    def replace(
        self, 
        year: int = None,
        month: int = None, 
        day: int = None
    ) -> EconoDate:
        """
        Return a new EconoDate object with the specified components replaced.

        This method creates a new EconoDate, using the current date as a template. Any
        component (year, month, or day) not provided will default to the corresponding
        value of this EconoDate.

        Parameters
        ----------
        year : int, optional
            The new year value. If not provided, the current year is used.
        month : int, optional
            The new month value. If not provided, the current month is used.
        day : int, optional
            The new day value. If not provided, the current day is used.

        Returns
        -------
        EconoDate
            A new EconoDate object with the updated components.

        Examples
        --------
        >>> d = EconoDate(2021, 1, 1)
        >>> d.replace(month=2)
        EconoDate(2021, 2, 1)
        
        """
        
        year = year if year is not None else self.year
        month = month if month is not None else self.month
        day = day if day is not None else self.day
        return type(self)(year, month, day)
    
    def weekday(self) -> int:
        """Returns the day of the week.
        
        This method is not yet implemented.
        
        Raises
        ------
        NotImplementedError
            Always raised since this method is not implemented yet.
        
        """
        
        raise NotImplementedError("The 'weekday()' method is not implemented yet.")
