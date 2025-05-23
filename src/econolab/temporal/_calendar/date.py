"""...

...

"""

from __future__ import annotations

from functools import total_ordering
from typing import Sequence, Self

from ...core.meta import EconoMeta
from .duration import EconoCalendar, EconoDuration


class EconoCalendarWithDuration(EconoCalendar):
    EconoDuration: type[EconoDuration]


@total_ordering
class EconoDate(metaclass=EconoMeta):
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
    
    __slots__ = ("_year", "_month", "_day")
    
    EconoCalendar: type[EconoCalendarWithDuration]
    
    
    #################
    # Class Methods #
    #################
    
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        
        cls._verify_econocalendar_class()
    
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
        cls._verify_econocalendar_class()
        Calendar = cls.EconoCalendar
        
        if not isinstance(days, int):
            raise TypeError(
                f"'days' must be an int; gor type '{type(days).__name__}'"
            )
        elif days < 1:
            raise ValueError(
                f"'days' must be at least equal to 1, got {days!r}"
            )
        
        def _divmod(n: int, d: int | Sequence[int]) -> tuple[int, int]:
            if isinstance(d, int):
                return divmod(n, d)
            for i, dpm in enumerate(d):
                if n < dpm:
                    return i, n
                n -= dpm
            raise ValueError("Value exceeds total days in a year")
        
        days += Calendar.start_day - 1
        days += sum(Calendar.days_per_month_seq[:Calendar.start_month - 1])
        days += (Calendar.start_year - 1) * sum(Calendar.days_per_month_seq)
        
        year_offset, day_of_year = _divmod(days - 1, sum(Calendar.days_per_month_seq))
        month_offset, day_offset = _divmod(day_of_year, Calendar.days_per_month_seq)
        
        if (year := 1 + year_offset) > Calendar.max_year:
            raise ValueError(
                f"Too many days: {days} days exceeds "
                f"the maximum number of years ({Calendar.max_year})"
            )
        month = 1 + month_offset
        day = 1 + day_offset
        return cls(year, month, day)
    
    @classmethod
    def min(cls) -> EconoDate:
        Calendar = cls.EconoCalendar
        return cls(Calendar.start_year, Calendar.start_month, Calendar.start_day)
    
    @classmethod
    def max(cls) -> EconoDate:
        Calendar = cls.EconoCalendar
        last_month = len(Calendar.days_per_month_seq)
        last_day = Calendar.days_per_month_seq[-1]
        return cls(year=Calendar.max_year, month=last_month, day=last_day)
    
    @classmethod
    def _verify_econocalendar_class(cls):
        if not (Calendar := getattr(cls, "EconoCalendar", None)):
            raise AttributeError(f"'{cls.__name__}' has no 'EconoCalendar' attribute")
        elif not isinstance(Calendar, EconoCalendar):
            raise TypeError(
                f"'{cls.__name__}.EconoCalendar' is not a valid 'EconoCalendar' object"
            )
    
    
    ###################
    # Special Methods #
    ###################

    def __eq__(self, other: object) -> bool:
        return (
            (self.year, self.month, self.day) == (other.year, other.month, other.day)
            if isinstance(other, type(self)) else 
            False
        )
    
    def __lt__(self, other: EconoDate) -> bool:
        if isinstance(other, type(self)):
            return (self.year, self.month, self.day) < (other.year, other.month, other.day)
        return NotImplemented
    
    def __add__(self, other: EconoDuration) -> EconoDate:
        if (
            isinstance(other, EconoDuration) and
            self.EconoCalendar is other.EconoCalendar
        ):
            return type(self).from_days(self.to_days() + other.days)
        return NotImplemented
    
    __radd__ = __add__
    
    def __sub__(self, other: EconoDuration | EconoDate) -> EconoDate | EconoDuration:
        if (
            isinstance(other, EconoDuration) and
            self.EconoCalendar is other.EconoCalendar
        ):
            return type(self).from_days(self.to_days() - other.days)
        elif isinstance(other, type(self)):
            return self.EconoCalendar.EconoDuration(self.to_days() - other.to_days())
        return NotImplemented
    
    def __hash__(self) -> int:
        return hash((self.year, self.month, self.day))
    
    def __new__(cls, *args, **kwargs) -> Self:
        cls._verify_econocalendar_class()
        return super().__new__(cls)
    
    def __init__(self, year: int, month: int, day: int) -> None:
        Calendar = self.EconoCalendar
        max_month = sum(Calendar.days_per_month_seq)
        max_day = Calendar.days_per_month_seq[month - 1]
        
        if not Calendar.start_year <= year <= Calendar.max_year:
            raise ValueError(f"'year' must be between {Calendar.start_year} and {Calendar.max_year}")
        if not 1 <= month <= max_month:
            raise ValueError(f"'month' must be between 1 and {max_month}")
        if not 1 <= day <= max_day:
            raise ValueError(f"'day' must be between 1 and {max_day}")

        self._year = year
        self._month = month
        self._day = day
    
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(year={self.year}, month={self.month}, day={self.day})"
        )
    
    def __str__(self) -> str:
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
        Calendar = self.EconoCalendar
        return (
            self.day
            + sum(Calendar.days_per_month_seq[:self.month - 1])
            + (self.year - Calendar.start_year) * sum(Calendar.days_per_month_seq)
        )
    
    def replace(
        self,
        *, 
        year: int | None= None,
        month: int | None = None, 
        day: int | None = None
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
        year = year or self.year
        month = month or self.month
        day = day or self.day
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
