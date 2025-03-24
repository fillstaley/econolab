"""...
"""


from __future__ import annotations
from functools import total_ordering

from .config import MINYEAR, MAXYEAR, DAYS_PER_WEEK, DAYS_PER_MONTH, MONTHS_PER_YEAR


@total_ordering
class EconoDate:
    """...
    """
    
    
    #################
    # Class Methods #
    #################
    
    @classmethod
    def from_days(cls, days: int) -> EconoDate:
        year = MINYEAR + days // (DAYS_PER_MONTH * MONTHS_PER_YEAR)
        if year > MAXYEAR:
            raise ValueError("too many days, exceeds maximum number of years")
        
        month = 1 + days % (DAYS_PER_MONTH * MONTHS_PER_YEAR) // DAYS_PER_MONTH
        day = 1 + days % DAYS_PER_MONTH
        return cls(year, month, day)
    
    
    ###############
    # Init Method #
    ###############
    
    def __init__(self, year: int, month: int, day: int):
        if not MINYEAR <= year <= MAXYEAR:
            raise ValueError(f"year must be between {MINYEAR} and {MAXYEAR}")
        if not 1 <= month <= MONTHS_PER_YEAR:
            raise ValueError(f"month must be between 1 and {MONTHS_PER_YEAR}")
        if not 1 <= day <= DAYS_PER_MONTH:
            raise ValueError(f"day must be between 1 and {DAYS_PER_MONTH}")
        
        self._year = year
        self._month = month
        self._day = day
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def year(self) -> int:
        return self._year
    
    @year.setter
    def year(self, value: int) -> None:
        raise AttributeError("readonly attribute")
    
    @property
    def month(self) -> int:
        return self._month
    
    @month.setter
    def month(self, value: int) -> None:
        raise AttributeError("readonly attribute")
    
    @property
    def day(self) -> int:
        return self._day
    
    @day.setter
    def day(self, value: int) -> None:
        raise AttributeError("readonly attribute")
    
    
    ###########
    # Methods #
    ###########
    
    def to_days(self) -> int:
        return (self.year - MINYEAR) * MONTHS_PER_YEAR * DAYS_PER_MONTH + (self.month - 1) * DAYS_PER_MONTH + self.day
    
    def replace(self, year: int = None, month: int = None, day: int = None) -> EconoDate:
        year = year if year is not None else self.year
        month = month if month is not None else self.month
        day = day if day is not None else self.day
        return EconoDate(year, month, day)
    
    def weekday(self) -> int:
        pass
    
    
    ###################
    # Special Methods #
    ###################

    def __eq__(self, other: EconoDate) -> bool:
        if isinstance(other, EconoDate):
            return (self.year, self.month, self.day) == (other.year, other.month, other.day)
        return NotImplemented

    def __lt__(self, other: EconoDate) -> bool:
        if isinstance(other, EconoDate):
            return (self.year, self.month, self.day) < (other.year, other.month, other.day)
        return NotImplemented
    
    def __add__(self, other: EconoDuration) -> EconoDate:
        if isinstance(other, EconoDuration):
            return EconoDate.from_days(self.to_days() + other.days)
        return NotImplemented
    
    __radd__ = __add__
    
    def __sub__(self, other: EconoDuration | EconoDate) -> EconoDate | EconoDuration:
        if isinstance(other, EconoDuration):
            return EconoDate.from_days(self.to_days() - other.days)
        elif isinstance(other, EconoDate):
            return EconoDuration(self.to_days() - other.to_days())
        return NotImplemented
    
    __rsub__ = __sub__
    
    def __repr__(self):
        return f"EconoDate({self.steps})"


@total_ordering
class EconoDuration:
    """...
    """
    
    ###############
    # Init Method #
    ###############
    
    def __init__(self, days: int = 0, weeks: int = 0):
        self._days = days + weeks * DAYS_PER_WEEK
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def days(self) -> int:
        return self._days
    
    @days.setter
    def days(self, value: int) -> None:
        raise AttributeError("readonly attribute")
    
    
    ###################
    # Special Methods #
    ###################
    
    def __eq__(self, other: EconoDuration) -> bool:
        if isinstance(other, EconoDuration):
            return self.days == other.days
        return NotImplemented

    def __lt__(self, other: EconoDuration) -> bool:
        if isinstance(other, EconoDuration):
            return self.days < other.days
        return NotImplemented
    
    def __bool__(self) -> bool:
        return bool(self.days)

    def __add__(self, other: EconoDuration) -> EconoDuration:
        if isinstance(other, EconoDuration):
            return EconoDuration(self.days + other.days)
        return NotImplemented

    def __sub__(self, other: EconoDuration) -> EconoDuration:
        if isinstance(other, EconoDuration):
            return EconoDuration(self.days - other.days)
        return NotImplemented

    def __repr__(self):
        return f"EconoStep({self.steps})"