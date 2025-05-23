"""...

...

"""

from __future__ import annotations

from functools import total_ordering
from typing import Sequence, Protocol, runtime_checkable

from numpy import floor

from ...core.meta import EconoMeta


@runtime_checkable
class EconoCalendar(Protocol):
    days_per_week: int
    days_per_month_seq: Sequence[int]
    start_year: int
    start_month: int
    start_day: int
    max_year: int


@total_ordering
class EconoDuration(metaclass=EconoMeta):
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
    
    __slots__ = ("_days",)
    
    EconoCalendar: type[EconoCalendar]
    
    
    #################
    # Class Methods #
    #################
    
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        
        cls._verify_econocalendar_class()
    
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
            self.days == other.days
            if isinstance(other, type(self)) else
            False
        )

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
            q = self // other
            r = self % other
            if not isinstance(q, int):
                raise TypeError(
                    f"Expected quotient to be of type 'int'; "
                    f"got type '{type(q).__name__}'"
                )
            return q, r
        return NotImplemented
    
    def __neg__(self) -> EconoDuration:
        return type(self)(-self.days)
    
    def __pos__(self) -> EconoDuration:
        return self
    
    def __abs__(self) -> EconoDuration:
        return type(self)(abs(self.days))
    
    def __hash__(self) -> int:
        return hash(self._days)
    
    def __new__(cls, *args, **kwargs) -> EconoDuration:
        if cls is EconoDuration:
            raise TypeError(
                "EconoDuration is an abstract base class; "
                "it cannot be instantiated directly."
            )
        return super().__new__(cls)
    
    def __init__(self, days: int | float = 0, *, weeks: int | float = 0) -> None:
        self._days = int(
            floor(days + weeks * self.EconoCalendar.days_per_week)
        )

    def __repr__(self) -> str:
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
