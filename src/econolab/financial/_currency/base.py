"""...

...

"""


# from __future__ import annotations

from functools import total_ordering
from numbers import Real
from re import search
from typing import Literal, Self



@total_ordering
class EconoCurrency:
    """...
    
    ...
    
    Note
    ----
    Equality is defined by tolerance (precision), but float rounding
    used in hashing may not always align with that. As a result, two values
    that compare equal may hash differently. This violates the hash/eq contract
    in edge cases. This will be resolved in a future version using Decimal.
    
    """
    
    __slots__ = ("_amount",)
    
    code: str
    symbol: str
    unit_name: str
    unit_plural: str
    full_name: str
    precision: int
    symbol_position: Literal["prefix", "suffix"]
    
    
    #################
    # Class Methods #
    #################
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        
        required_attrs = {
            "code",
            "symbol",
            "unit_name",
            "unit_plural",
            "precision",
            "symbol_position",
        }
        
        if missing := [
            attr for attr in required_attrs if not hasattr(cls, attr)
        ]:
            raise TypeError(
                f"Can't create EconoCurrency subclass {cls.__name__}; "
                f"missing attributes: {missing}"
            )
    
    
    ###################
    # Special Methods #
    ###################
    
    # TODO: add tests for proper equality relative to precision
    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return (self - other).is_zero()
        return NotImplemented
    
    def __lt__(self, other) -> bool:
        if isinstance(other, type(self)):
            return (self - other).is_negative()
        return NotImplemented
    
    def __hash__(self):
        return hash((type(self), round(self.amount, self.precision)))
    
    def __bool__(self) -> bool:
        return bool(self.amount)
    
    def __add__(self, other: Self) -> Self:
        if isinstance(other, type(self)):
            return type(self)(self.amount + other.amount)
        return NotImplemented
    
    def __sub__(self, other: Self) -> Self:
        if isinstance(other, type(self)):
            return type(self)(self.amount - other.amount)
        return NotImplemented
    
    def __mul__(self, other: Real) -> Self:
        if isinstance(other, Real):
            return type(self)(self.amount * other)
        return NotImplemented
    
    __rmul__ = __mul__
    
    def __truediv__(self, other: Self | Real) -> float | Self:
        if isinstance(other, type(self)):
            return self.amount / other.amount
        elif isinstance(other, Real):
            return type(self)(self.amount / other)
        return NotImplemented
    
    def __floordiv__(self, other: Self | Real) -> float | Self:
        if isinstance(other, type(self)):
            return self.amount // other.amount
        elif isinstance(other, Real):
            return type(self)(self.amount // other)
        return NotImplemented
    
    def __mod__(self, other: Self) -> Self:
        if isinstance(other, type(self)):
            return type(self)(self.amount % other.amount)
        return NotImplemented
    
    def __divmod__(self, other: Self) -> tuple[float, Self]:
        if isinstance(other, type(self)):
            return self // other, self % other
        return NotImplemented
    
    def __neg__(self) -> Self:
        return type(self)(-self.amount)
    
    def __pos__(self) -> Self:
        return type(self)(self.amount)
    
    def __abs__(self) -> Self:
        return type(self)(abs(self.amount))
    
    def __int__(self) -> int:
        return int(self.amount)
    
    def __float__(self) -> int:
        return float(self.amount)
    
    def __round__(self, ndigits: int | None = None) -> float:
        return round(self.amount, ndigits if ndigits is not None else self.precision)
    
    def __new__(cls, *args, **kwargs):
        if cls is EconoCurrency:
            raise TypeError(
                "EconoCurrency is an abstract base class; "
                "it cannot be instantiated directly.")
        return super().__new__(cls)
    
    def __init__(self, amount: Real = 0, /) -> None:
        self._amount = float(amount)
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.amount})"
    
    def __str__(self) -> str:
        return self.to_string(with_units=False)
    
    # TODO: introduce a custom format type for symbol/units
    # TODO: add tests for formatting
    def __format__(self, format_spec: str) -> str:
        return self.format_with_symbol(format_spec)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def amount(self) -> float:
        """The amount of currency."""
        return self._amount
    
    @amount.setter
    def amount(self, _: float) -> None:
        raise AttributeError("readonly attribute")
    
    
    ###########
    # Methods #
    ###########
    
    # TODO: add tests for these comparison methods
    def is_zero(self) -> bool:
        """Return True if the currency amount is zero, relative to its precision."""
        return self.is_positive_or_zero() and self.is_negative_or_zero()

    def is_positive_or_zero(self) -> bool:
        """Return True if the currency amount is greater than or equal to zero.
        
        Uses the currency's precision to compare against a small negative number.
        """
        return self.amount > -10 ** -self.precision

    def is_negative_or_zero(self) -> bool:
        """Return True if the currency amount is less than or equal to zero.
        
        Uses the currency's precision to compare against a small positive number.
        """
        return self.amount < 10 ** -self.precision
    
    def is_positive(self) -> bool:
        """Return True if the currency amount is greater than zero.
        
        Uses the currency's precision to compare against a small positive number.
        """
        return self.amount >= 10 ** -self.precision
    
    def is_negative(self) -> bool:
        """Return True if the currency amount is less than zero.
        
        Uses the currency's precision to compare against a small negative number.
        """
        return self.amount <= -10 ** -self.precision
    
    def to_string(self, *, with_units: bool = False) -> str:
        return (
            self.format_with_units() if with_units else self.format_with_symbol()
        )
    
    def format_with_symbol(self, format_spec: str | None = None) -> str:
        """Formats the currency amount as a string with the currency's symbol.

        Parameters
        ----------
        format_spec : str, optional
            A format specification string.
        
        Returns
        -------
        str
            Formatted string with currency symbol.
        """
        fs = self._apply_precision_default(format_spec or "", self.precision)
        rounded = format(self.amount, fs)
        if self.symbol_position == "prefix":
            return f"{self.symbol}{rounded}"
        return f"{rounded} {self.symbol}"
    
    def format_with_units(self, format_spec: str | None = None) -> str:
        """Formats the currency amount as a string with the currency's units.
        
        The singular (ie. 'unit_name') or plural form is used appropriately.
        
        Parameters
        ----------
        format_spec : str, optional
            A format specification string.
        
        Returns
        -------
        str
            Formatted string with currency units.
        """
        fs = self._apply_precision_default(format_spec or "", self.precision)
        rounded = format(self.amount, fs)
        unit = (
            self.unit_name if abs(self.amount - 1) < 10 ** -self.precision else
            self.unit_plural
        )
        return f"{rounded} {unit}"
    
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def _apply_precision_default(format_spec: str, default_precision: int) -> str:
        """Inserts the currency's precision into a format spec string."""
        if not search(r"\.\d", format_spec):
            # Inject .{default_precision} just before type code if present
            match = search(r"[a-zA-Z]$", format_spec)
            if match:
                i = match.start()
                return f"{format_spec[:i]}.{default_precision}{format_spec[i:]}"
            else:
                return f"{format_spec}.{default_precision}f"
        return format_spec
