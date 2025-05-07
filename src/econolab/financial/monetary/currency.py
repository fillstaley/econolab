"""...

...

"""


from __future__ import annotations

import logging
logger = logging.getLogger(__name__)

from dataclasses import dataclass, field
from functools import total_ordering
from numbers import Real
from typing import Literal, Protocol, Self, runtime_checkable


@runtime_checkable
class EconoModel(Protocol):
    pass


@dataclass(frozen=True, slots=True)
class CurrencySpecification:
    """...
    
    ...
    
    """
    name: str
    symbol: str
    unit_name: str | None = None
    unit_plural: str | None = None
    precision: int = 2
    symbol_position: Literal["prefix", "suffix"] = "prefix"
    
    
    def __post_init__(self) -> None:
        # validate the provided name
        if not isinstance(self.name, str):
            raise TypeError(
                f"'name' must be a non-empty string; got {type(self.name).__name__}."
            )
        elif not self.name.strip():
            raise ValueError("'name' must be a non-empty string.")
        
        # validate the provided symbol
        if not isinstance(self.symbol, str):
            raise TypeError(
                f"'symbol' must be a non-empty string; got {type(self.symbol).__name__}."
            )
        elif not self.symbol.strip():
            raise ValueError("'symbol' must be a non-empty string.")
        
        # validate the unit_name
        if self.unit_name is None:
            object.__setattr__(self, "unit_name", self.name.lower())
        if not isinstance(self.unit_name, str):
            raise TypeError(
                f"'unit_name' must be a non-empty string when provided; "
                f"got {type(self.unit_name).__name__}."
            )
        elif not self.unit_name.strip():
            raise ValueError("'unit_name' must be a non-empty string when provided.")
        
        # validate the unit_plural
        if self.unit_plural is None:
            object.__setattr__(self, "unit_plural", self.default_plural(self.unit_name))
        elif not isinstance(self.unit_plural, str):
            raise TypeError(
                f"'unit_plural' must be a non-empty string when provided; "
                f"got {type(self.unit_plural).__name__}."
            )
        elif not self.unit_plural.strip():
            raise ValueError("'unit_plural' must be a non-empty string when provided.")
        
        # validate the precision
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
        
        # validate the symbol_position
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
    
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def default_plural(unit_name: str) -> str:
        """Return the default plural form of a unit name by appending 's'."""
        return f"{unit_name}s"


@total_ordering
class EconoCurrency:
    """...
    
    ...
    
    """
    
    _model: EconoModel
    
    name: str
    symbol: str
    unit_name: str
    unit_plural: str
    precision: int
    symbol_position: Literal["prefix", "suffix"]
    
    
    #################
    # Class Methods #
    #################
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        required_attrs = [
            "name",
            "symbol",
            "unit_name",
            "unit_plural",
            "precision",
            "symbol_position",
        ]
        if missing := [attr for attr in required_attrs if not hasattr(cls, attr)]:
            raise TypeError(
                f"Can't create EconoCurrency subclass {cls.__name__}; "
                f"missing attributes: {missing}"
            )
    
    
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
    name="American Dollar",
    symbol="$",
    unit_name="dollar",
)

JPY_SPECIFICATION = CurrencySpecification(
    name="Japanese Yen",
    symbol="¥",
    unit_name="yen",
    unit_plural="yen",
    precision=0
)

SEK_SPECIFICATION = CurrencySpecification(
    name="Swedish Krona",
    symbol="kr",
    unit_name="krona",
    unit_plural="kronor",
    symbol_position="suffix"
)

DEFAULT_CURRENCY_SPECIFICATION = USD_SPECIFICATION
