"""Defines the Currency class for modeling monetary units of account.

This module is part of the financial infrastructure of the EconoLab project.
It provides a simple way to handle formatting, naming, and rounding behavior
for different currencies used throughout the model.

"""

from __future__ import annotations
from typing import Literal


class Currency:
    """A monetary unit of account.

    The Currency class represents a unit of account used to denominate values 
    in an economic model. It supports consistent string formatting, rounding 
    precision, and naming conventions for both singular and plural forms.

    Examples
    --------
    >>> usd = Currency(name="Dollar", symbol="$")
    >>> usd(5.5)
    '$5.50'

    >>> jpy = Currency(name="Yen", unit_name="yen", symbol="¥", precision=0)
    >>> jpy(1200)
    '¥1200'
    
    """
    
    __slots__ = (
        "name",
        "unit_name",
        "unit_plural",
        "symbol",
        "symbol_position",
        "precision",
    )
    
    DEFAULT_SYMBOL = "$"
    DEFAULT_PRECISION = 2

    def __eq__(self, other: Currency) -> bool:
        if isinstance(other, Currency):
            return (self.name, self.unit_name, self.symbol) == (other.name, other.unit_name, other.symbol)
        return NotImplemented
    
    def __hash__(self) -> int:
        return hash((self.name, self.unit_name, self.symbol))
    
    def __init__(self,
        name: str,
        unit_name: str | None = None,
        unit_plural: str | None = None,
        symbol: str | None = None,
        symbol_position: Literal["prefix", "suffix"] = "prefix",
        precision: int | None = None,
    ) -> None:
        
        if symbol_position not in {"prefix", "suffix"}:
            raise ValueError("'symbol_position' must be either 'prefix' or 'suffix'.")
        if precision is not None and isinstance(precision, int) and precision < 0:
            raise ValueError("'precision' must be a nonnegative integer or 'None'.")
        
        self.name = name
        self.unit_name = unit_name or self.name.lower()
        self.unit_plural = unit_plural or self.default_plural(self.unit_name)
        self.symbol = symbol or self.DEFAULT_SYMBOL
        self.symbol_position = symbol_position
        self.precision = self.DEFAULT_PRECISION if precision is None else precision

    def __repr__(self) -> str:
        return (
            f"Currency(name='{self.name}', unit_name='{self.unit_name}', "
            f"         unit_plural='{self.unit_plural}', symbol='{self.symbol}', "
            f"         symbol_position='{self.symbol_position}', precision={self.precision})"
        )
    
    def __str__(self) -> str:
        return f"{self.name}"
    
    def __format__(self, format_spec: str) -> str:
        return str(self).__format__(format_spec)
    
    def __call__(self, amount: float, use_units: bool = False) -> str:
        """Return a formatted string representation of the given amount in the calling currency. 

        Parameters
        ----------
        amount : float
            The monetary amount to format.
        use_units : bool, optional
            Whether to use unit names instead of currency symbol; defaults to False.
            Singular/plural logic applies based on whether the (rounded) amount equals 1.0,
            within the currency precision.

        Returns
        -------
        str
            The formatted currency string.
        """
        if use_units:
            return self.format_with_units(
                amount,
                self.precision,
                self.unit_name,
                self.unit_plural
            )
        return self.format_with_symbol(
            amount,
            self.precision,
            self.symbol,
            self.symbol_position
        )
    
    
    @staticmethod
    def default_plural(unit_name: str) -> str:
        """Return the default plural form of a unit name by appending 's'."""
        return f"{unit_name}s"
    
    @staticmethod
    def format_with_symbol(
        amount: float,
        precision: int,
        symbol: str,
        position: Literal["prefix", "suffix"]
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

        Returns
        -------
        str
            Formatted string with currency symbol.
        """
        rounded = round(amount, precision)
        if position == "prefix":
            return f"{symbol}{rounded:.{precision}f}"
        return f"{rounded:.{precision}f}{symbol}"
    
    @staticmethod
    def format_with_units(
        amount: float,
        precision: int,
        unit_singular: str,
        unit_plural: str
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

        Returns
        -------
        str
            Formatted string with appropriate unit name.
        """
        rounded = round(amount, precision)
        unit = unit_singular if abs(rounded - 1) < 10 ** -precision else unit_plural
        return f"{rounded:.{precision}f} {unit}"