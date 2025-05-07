"""...

...

"""


from dataclasses import dataclass, field
from typing import Literal, Protocol, runtime_checkable


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
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(self) -> None:
        pass
    
    def __repr__(self) -> str:
        pass


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
