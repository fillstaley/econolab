"""...

...

"""


from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from numbers import Real
from re import fullmatch, search
from typing import Literal, Self


@dataclass(frozen=True, slots=True)
class CurrencySpecification:
    """...
    
    ...
    
    """
    code: str
    symbol: str
    unit_name: str
    unit_plural: str | None = None
    full_name: str | None = None
    precision: int = 2
    symbol_position: Literal["prefix", "suffix"] = "prefix"
    
    
    def __post_init__(self) -> None:
        # validate code arg
        if not isinstance(self.code, str):
            raise TypeError(
                f"'code' must be a string of three uppercase letters; "
                f"got {type(self.code).__name__}."
            )
        elif not self.code.strip():
            raise ValueError(
                "'code' must be a string of three uppercase letters; it cannot be empty."
            )
        elif not fullmatch(r"[A-Z]{3}", self.code):
            raise ValueError(
                f"'code' must match the format 'XXX' (three uppercase letters); "
                f"got '{self.code}'."
            )
        
        # validate symbol arg
        if not isinstance(self.symbol, str):
            raise TypeError(
                f"'symbol' must be a non-empty string; got {type(self.symbol).__name__}."
            )
        elif not self.symbol.strip():
            raise ValueError("'symbol' must be a non-empty string.")
        
        # validate and normalize unit_name arg
        if not isinstance(self.unit_name, str):
            raise TypeError(
                f"'unit_name' must be a non-empty string; "
                f"got {type(self.unit_name).__name__}."
            )
        elif not self.unit_name.strip():
            raise ValueError("'unit_name' must be a non-empty string.")
        object.__setattr__(self, "unit_name", self.unit_name.lower())

        # validate and normalize unit_plural arg
        if self.unit_plural is None:
            object.__setattr__(self, "unit_plural", f"{self.unit_name}s")
        if not isinstance(self.unit_plural, str):
            raise TypeError(
                f"'unit_plural' must be a non-empty string when provided; "
                f"got {type(self.unit_plural).__name__}."
            )
        elif not self.unit_plural.strip():
            raise ValueError("'unit_plural' must be a non-empty string when provided.")
        object.__setattr__(self, "unit_plural", self.unit_plural.lower())
        
        # validate full_name arg
        if self.full_name is None:
            object.__setattr__(self, "full_name", self.unit_name.title())
        if not isinstance(self.full_name, str):
            raise TypeError(
                f"'full_name' must be a non-empty string when provided; "
                f"got {type(self.full_name).__name__}."
            )
        elif not self.full_name.strip():
            raise ValueError("'full_name' must be a non-empty string when provided.")
        
        # validate precision arg
        if not isinstance(self.precision, int):
            raise TypeError(
                f"'precision' must be a non-negative integer; "
                f"got {type(self.precision).__name__}."
            )
        elif self.precision < 0:
            raise ValueError(
                f"'precision' must be a non-negative integer when provided; "
                f"got {self.precision}."
            )
        
        # validate symbol_position arg
        if self.symbol_position not in ("prefix", "suffix"):
            raise ValueError(
                f"'symbol_position' must be either 'prefix' or 'suffix'; "
                f"got {self.symbol_position}."
            )
    
    
    ###########
    # Methods #
    ###########
    
    def to_dict(self) -> dict:
        return {slot: getattr(self, slot) for slot in self.__slots__}


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


USD_SPECIFICATION = CurrencySpecification(
    code="USD",
    symbol="$",
    unit_name="dollar",
    full_name="US Dollar"
)

JPY_SPECIFICATION = CurrencySpecification(
    code="JPY",
    symbol="¥",
    unit_name="yen",
    unit_plural="yen",
    full_name="Japanese Yen",
    precision=0
)

SEK_SPECIFICATION = CurrencySpecification(
    code="SEK",
    symbol="kr",
    unit_name="krona",
    unit_plural="kronor",
    full_name="Swedish Krona",
    symbol_position="suffix"
)

DEFAULT_CURRENCY_SPECIFICATION = USD_SPECIFICATION
