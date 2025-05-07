"""...

...

"""


from __future__ import annotations

import logging
logger = logging.getLogger(__name__)

from dataclasses import dataclass, field
from functools import total_ordering
from numbers import Real
from re import fullmatch
from typing import Literal, Protocol, Self, runtime_checkable


@runtime_checkable
class EconoModel(Protocol):
    pass


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
    
    """
    
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
        
        if missing := [
            attr for attr in cls.required_cls_attrs() if not hasattr(cls, attr)
        ]:
            raise TypeError(
                f"Can't create EconoCurrency subclass {cls.__name__}; "
                f"missing attributes: {missing}"
            )
    
    @classmethod
    def required_cls_attrs(cls) -> set[str]:
        return {
            "code",
            "symbol",
            "unit_name",
            "unit_plural",
            "precision",
            "symbol_position",
        }
    
    
    ###################
    # Special Methods #
    ###################
    
    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.amount == other.amount
        return NotImplemented
    
    def __lt__(self, other) -> bool:
        if isinstance(other, type(self)):
            return self.amount < other.amount
        return NotImplemented
    
    def __hash__(self):
        return hash((type(self), self.amount))
    
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
    
    def __floordiv__(self, other: Self | int) -> int | Self:
        if isinstance(other, type(self)):
            return self.amount // other.amount
        elif isinstance(other, int):
            return type(self)(self.amount // other)
        return NotImplemented
    
    def __mod__(self, other: Self) -> Self:
        if isinstance(other, type(self)):
            return type(self)(self.amount % other.amount)
        return NotImplemented
    
    def __divmod__(self, other: Self) -> tuple[int, Self]:
        if isinstance(other, type(self)):
            return self // other, self % other
        return NotImplemented
    
    def __neg__(self) -> Self:
        return type(self)(-self.amount)
    
    def __pos__(self) -> Self:
        return type(self)(self.amount)
    
    def __abs__(self) -> Self:
        return type(self)(abs(self.amount))
    
    def __new__(cls, *args, **kwargs):
        if cls is EconoCurrency:
            raise TypeError("EconoCurrency is an abstract base class and cannot be instantiated directly.")
        return super().__new__(cls, *args, **kwargs)
    
    def __init__(self, amount: Real = 0) -> None:
        self._amount = float(amount)
    
    def __repr__(self) -> str:
        return f"{self._model.name}.{type(self).__name__}(amount={self.amount})"
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @amount.setter
    def amount(self, _: float) -> None:
        raise AttributeError("readonly attribute")
    
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def format_with_symbol(
        amount: float,
        precision: int,
        symbol: str,
        position: Literal["prefix", "suffix"],
        format_spec: str | None = None
    ) -> str:
        """Format a numeric amount with a currency symbol.

        Parameters
        ----------
        amount : float
            The amount to format.
        precision : int
            Number of decimal places to round to.
        symbol : str
            The currency symbol to use.
        position : {'prefix', 'suffix'}
            Whether the symbol appears before or after the number.
        format_spec : str, optional
            A format specification string. (Currently ignored.)
        
        Returns
        -------
        str
            Formatted string with currency symbol.
        """
        # FIXME: format_spec is currently ignored.
        # In future versions, this should control formatting precision and style.
        if format_spec:
            logger.debug(
                f"Ignoring format_spec='{format_spec}' in Currency.format_with_symbol()."
            )
        
        rounded = round(amount, precision)
        if position == "prefix":
            return f"{symbol}{rounded:.{precision}f}"
        return f"{rounded:.{precision}f} {symbol}"
    
    @staticmethod
    def format_with_units(
        amount: float,
        precision: int,
        unit_singular: str,
        unit_plural: str,
        format_spec: str | None = None
    ) -> str:
        """Format a numeric amount with singular or plural currency units.

        Parameters
        ----------
        amount : float
            The amount to format.
        precision : int
            Number of decimal places to round to.
        unit_singular : str
            The singular form of the currency unit.
        unit_plural : str
            The plural form of the currency unit.
        format_spec : str, optional
            A format specification string. (Currently ignored.)
        
        Returns
        -------
        str
            Formatted string with appropriate unit name.
        """
        # FIXME: format_spec is currently ignored.
        # In future versions, this should control formatting precision and style.
        if format_spec:
            logger.debug(
                f"Ignoring format_spec='{format_spec}' in Currency.format_with_units()."
            )
        
        rounded = round(amount, precision)
        unit = unit_singular if abs(rounded - 1) < 10 ** -precision else unit_plural
        return f"{rounded:.{precision}f} {unit}"


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
