"""...

...

"""

from dataclasses import dataclass
from re import fullmatch
from typing import Literal


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
