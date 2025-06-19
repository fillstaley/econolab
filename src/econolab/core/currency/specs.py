"""...

...

"""

from __future__ import annotations

from dataclasses import dataclass
from re import fullmatch
from typing import Literal


@dataclass(frozen=True, slots=True)
class CurrencySpecification:
    """Immutable metadata structure for defining a currency's formal attributes.

    This class is used to specify the identifying features and formatting rules
    for a currency. These specifications can then be used to construct or bind
    model-specific currency classes derived from `EconoCurrency`.

    Typical usage involves defining constants like `USD_SPECIFICATION` or 
    `JPY_SPECIFICATION`, which are passed to currency class factories 
    or bound to models.

    Attributes
    ----------
    code : str
        ISO-style currency code (e.g., "USD", "JPY").
    symbol : str
        Symbol used for display purposes (e.g., "$", "¥").
    unit_name : str
        Singular form of the currency unit (e.g., "dollar").
    unit_plural : str, optional
        Plural form of the unit (e.g., "dollars"). Defaults to unit_name + "s".
    full_name : str, optional
        Descriptive name (e.g., "US Dollar"). Defaults to title-cased unit_name.
    precision : int, optional
        Number of decimal places to round/display. Defaults to 2.
    symbol_position : {"prefix", "suffix"}, optional
        Whether the symbol appears before or after the number. Defaults to "prefix".
    """
    code: str = "ELD"
    symbol: str = "$"
    unit_name: str = "dollar"
    unit_plural: str | None = None
    full_name: str | None = None
    precision: int = 2
    symbol_position: Literal["prefix", "suffix"] = "prefix"
    
    
    def __post_init__(self) -> None:
        """Validates and normalizes fields after initialization.

        This method ensures that all provided attributes conform to expected 
        formats (e.g., `code` is three uppercase letters, `symbol` is non-empty). 
        It also sets default values for `unit_plural` and `full_name` if they 
        are not explicitly provided.

        Raises
        ------
        TypeError
            If any field is of the wrong type.
        ValueError
            If any field is missing or improperly formatted.
        """
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


# Predefined specification for the US Dollar (USD)
USD_SPECIFICATION = CurrencySpecification(
    code="USD",
    symbol="$",
    unit_name="dollar",
    full_name="US Dollar"
)

# Predefined specification for the Japanese Yen (JPY)
JPY_SPECIFICATION = CurrencySpecification(
    code="JPY",
    symbol="¥",
    unit_name="yen",
    unit_plural="yen",
    full_name="Japanese Yen",
    precision=0
)

# Predefined specification for the Swedish Krona (SEK)
SEK_SPECIFICATION = CurrencySpecification(
    code="SEK",
    symbol="kr",
    unit_name="krona",
    unit_plural="kronor",
    full_name="Swedish Krona",
    symbol_position="suffix"
)
