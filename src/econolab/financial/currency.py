"""Defines the Currency class for modeling monetary units of account.

This module is part of the financial infrastructure of the EconoLab project.
It provides a simple way to handle formatting, naming, and rounding behavior
for different currencies used throughout the model.

"""

from __future__ import annotations
from typing import Literal
import logging

logger = logging.getLogger(__name__)


class Currency:
    """A monetary unit of account used for formatting and symbolic representation of money.

    The Currency class represents a unit of account used to denominate values 
    in an economic model. It supports consistent string formatting, rounding 
    precision, and naming conventions for both singular and plural forms.
    
    Attributes
    ----------
    name : str
        The canonical name of the currency. Required and used to uniquely identify it.
    unit_name : str
        Optional singular form of the currency unit (e.g., "dollar"). Defaults to a
        lowercase version of `name`.
    unit_plural : str
        Optional plural form of the currency unit (e.g., "dollars"). Defaults to
        `Currency.default_plural(unit_name)`, which is defined to append 's' by default.
    symbol : str
        Optional currency symbol (e.g., "$"). Defaults to class attribute `DEFAULT_SYMBOL`.
    symbol_position : {'prefix', 'suffix'}
        Optional indicator of whether the symbol appears before or after the number.
        Defaults to "prefix".
    precision : int
        Optional number of decimal places used for rounding amounts. Defaults to
        `DEFAULT_PRECISION`. Must be nonnegative.
    
    Note
    ----
    This class uses a registry to ensure that only one instance of each currency
    (by normalized name) exists at runtime. Attempts to create a Currency with an
    existing name will return the existing instance and skip reinitialization.
    
    Examples
    --------
    >>> usd = Currency(name="Dollar", symbol="$")
    >>> usd(5.5)
    '$5.50'
    
    >>> also_usd = Currency(name="Dollar")
    >>> usd is also_usd
    True
    
    >>> jpy = Currency(name="Yen", unit_name="yen", symbol="¥", precision=0)
    >>> jpy(1200.1)
    '¥1200'
    """
    
    __slots__ = (
        "name",
        "unit_name",
        "unit_plural",
        "symbol",
        "symbol_position",
        "precision",
        "_initialized",
    )
    
    DEFAULT_SYMBOL: str = "$"  # Default currency symbol if none is provided
    DEFAULT_PRECISION: int = 2  # Default decimal precision used for formatting and rounding
    
    _instances: dict[str, Currency] = {} # Registry of Currency instances indexed by normalized name
    
    
    #################
    # Class Methods #
    #################
    
    @classmethod
    def instances(cls) -> list[str]:
        """Return a list of currency names currently in the registry."""
        return list(cls._instances.keys())
    
    @classmethod
    def from_dict(cls, data: dict) -> Currency:
        """Create a Currency instance from a dictionary of attributes.

        Parameters
        ----------
        data : dict
            A dictionary with keys corresponding to Currency attributes.

        Returns
        -------
        Currency
            A new Currency instance initialized from the dictionary.
        
        Raises
        ------
        ValueError
            If the 'name' key is missing from the dictionary.
        """
        
        if not (name := data.get("name")):
            raise ValueError("Currency 'name' is required")
        return cls(
            name=name,
            unit_name=data.get("unit_name"),
            unit_plural=data.get("unit_plural"),
            symbol=data.get("symbol", cls.DEFAULT_SYMBOL),
            symbol_position=data.get("symbol_position", "prefix"),
            precision=data.get("precision", cls.DEFAULT_PRECISION),
        )
    
    
    ###################
    # Special Methods #
    ###################

    def __eq__(self, other: Currency) -> bool:
        if isinstance(other, Currency):
            return self.name == other.name
        return NotImplemented
    
    def __bool__(self) -> bool:
        return True
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def __new__(cls, name: str, *args, **kwargs) -> Currency:
        """Implements singleton-style behavior by reusing instances by normalized name."""
        # support positional arguments
        unit_name = kwargs.get("unit_name", args[0] if args else None)
        unit_plural = kwargs.get("unit_plural", args[1] if len(args) > 1 else None)
        symbol = kwargs.get("symbol", args[2] if len(args) > 2 else None)
        symbol_position = kwargs.get("symbol_position", args[3] if len(args) > 3 else "prefix")
        precision = kwargs.get("precision", args[4] if len(args) > 4 else None)

        cls._validate_new_args(name, unit_name, unit_plural, precision, symbol_position)
        normalized_name = cls._normalize_name(name)
        if normalized_name in cls._instances:
            logger.warning(
                f"Currency '{name}' already exists. Returning existing instance without reinitialization."
            )
            return cls._instances[normalized_name]
        instance = super().__new__(cls)
        cls._instances[normalized_name] = instance
        logger.info(f"Currency '{name}' registered.")
        return instance
    
    def __init__(self,
        name: str,
        unit_name: str | None = None,
        unit_plural: str | None = None,
        symbol: str | None = None,
        symbol_position: Literal["prefix", "suffix"] = "prefix",
        precision: int | None = None,
    ) -> None:
        # return early if already initialized
        if getattr(self, "_initialized", False):
            return
        
        self.name = name
        self.unit_name = unit_name or self.name.lower()
        self.unit_plural = unit_plural or self.default_plural(self.unit_name)
        self.symbol = symbol or self.DEFAULT_SYMBOL
        self.symbol_position = symbol_position
        self.precision = self.DEFAULT_PRECISION if precision is None else precision
        
        # mark the instance as initialized (to prevent reinitialization)
        self._initialized = True

    def __repr__(self) -> str:
        return (
            f"Currency(name='{self.name}', unit_name='{self.unit_name}', "
            f"unit_plural='{self.unit_plural}', symbol='{self.symbol}', "
            f"symbol_position='{self.symbol_position}', precision={self.precision})"
        )
    
    def __str__(self) -> str:
        return f"{self.name}"
    
    def __format__(self, format_spec: str) -> str:
        return str(self).__format__(format_spec)
    
    def __call__(
            self,
            amount: float, 
            format_spec: str | None = None,
            *,
            use_units: bool = False,
        ) -> str:
        """Return a formatted string representation of the given amount in the calling currency. 

        Parameters
        ----------
        amount : float
            The monetary amount to format.
        format_spec : str, optional
            A format specification string. (Currently ignored.)
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
                self.unit_plural,
                format_spec
            )
        return self.format_with_symbol(
            amount,
            self.precision,
            self.symbol,
            self.symbol_position,
            format_spec
        )
    
    
    ###########
    # Methods #
    ###########
    
    def to_dict(self) -> dict:
        """Return a dictionary representation of the Currency instance."""
        return {
            "name": self.name,
            "unit_name": self.unit_name,
            "unit_plural": self.unit_plural,
            "symbol": self.symbol,
            "symbol_position": self.symbol_position,
            "precision": self.precision,
        }
    
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def _validate_new_args(
        name: str,
        unit_name: str | None,
        unit_plural: str | None,
        precision: int | None,
        symbol_position: Literal["prefix", "suffix"]
    ) -> None:
        """Validate input arguments before creating a new Currency instance."""
        if not name or not name.strip():
            raise ValueError("Currency 'name' must be a non-empty string.")
        if unit_name is not None and not unit_name.strip():
            raise ValueError("'unit_name' must be a non-empty string if provided.")
        if unit_plural is not None and not unit_plural.strip():
            raise ValueError("'unit_plural' must be a non-empty string if provided.")
        if precision is not None and (not isinstance(precision, int) or precision < 0):
            raise ValueError("'precision' must be a nonnegative integer.")
        if symbol_position not in {"prefix", "suffix"}:
            raise ValueError(f"'symbol_position' must be either 'prefix' or 'suffix', got {symbol_position}.")
    
    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize the currency name by converting to lowercase and stripping whitespace."""
        return name.lower().strip()
    
    @staticmethod
    def default_plural(unit_name: str) -> str:
        """Return the default plural form of a unit name by appending 's'."""
        return f"{unit_name}s"
    
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
        return f"{rounded:.{precision}f}{symbol}"
    
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