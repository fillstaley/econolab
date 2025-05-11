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
    """Abstract base class for model-bound currency types in EconoLab models.

    This class defines the arithmetic behavior, comparison logic, and 
    formatting conventions for a model-specific currency. It acts like 
    a numeric type (similar to `float`), but with domain-specific semantics 
    and precision-aware operations tailored to currency usage.

    Subclasses must define a currency specification via class attributes, 
    such as `code`, `symbol`, `precision`, etc. These are typically derived 
    from a `CurrencySpecification` instance using a class factory or binding 
    method defined at the model level.

    EconoCurrency is designed to be subclassed dynamically per model 
    (e.g., USD in ModelA will be different from USD in ModelB) to enable 
    distinct monetary systems to coexist.

    Parameters
    ----------
    amount : Real, optional
        The numeric value of the currency. Defaults to 0.
    
    Note
    ----
    Equality is defined by tolerance (precision), but float rounding used
    in hashing may not always align with that. As a result, two values that
    compare equal may hash differently. This violates the hash/eq contract
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
    
    def register_format_type(*codes):
        def decorator(func):
            func._format_codes = set(codes)
            return func
        return decorator
    
    @classmethod
    @register_format_type("s", "f", "")
    def format_with_symbol(cls, amount: Real, format_spec: str = "") -> str:
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
        cls._validate_typeless_format(format_spec)
        
        rounded = format(*cls._ensure_precision(amount, format_spec))
        if cls.symbol_position == "prefix":
            return f"{cls.symbol}{rounded}"
        return f"{rounded} {cls.symbol}"
    
    @classmethod
    @register_format_type("u")
    def format_with_units(cls, amount: float, format_spec: str = "") -> str:
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
        cls._validate_typeless_format(format_spec)
        
        rounded = format(*cls._ensure_precision(amount, format_spec))
        unit = (
            cls.unit_name if abs(amount - 1) < 10 ** -cls.precision else
            cls.unit_plural
        )
        return f"{rounded} {unit}"
    
    @classmethod
    def _ensure_precision(
        cls,
        amount: Real,
        format_spec: str = ""
    ) -> tuple[float, str]:
        # If precision is specified in the format string, use it.
        # Otherwise, apply class precision and append it to the format spec.
        if (match := search(r"\.(\d+)", format_spec)):
            precision = int(match[1])
            format_spec += "f"
        else:
            precision = cls.precision
            format_spec += f".{precision}f"
            
        rounded = round(float(amount), precision)
        return rounded, format_spec
    
    
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
    
    # TODO: add tests for rounding
    def __round__(self, ndigits: int | None = None) -> Self:
        format_spec = f".{ndigits}" if ndigits is not None else ""
        rounded_amount, _ = self._ensure_precision(self.amount, format_spec)
        return type(self)(rounded_amount)
    
    def __new__(cls, *args, **kwargs):
        if cls is EconoCurrency:
            raise TypeError(
                "EconoCurrency is an abstract base class; "
                "it cannot be instantiated directly.")
        return super().__new__(cls)
    
    # TODO: improve the documentation here
    def __init__(self, amount: Real = 0, /) -> None:
        """Initialize a currency instance with a numeric amount.

        Parameters
        ----------
        amount : Real, optional
            The numeric value of the currency. Defaults to 0.

        Examples
        --------
        >>> usd = USD(10.5)
        >>> print(usd)
        $10.50
        """
        self._amount = float(amount)
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.amount})"
    
    def __str__(self) -> str:
        return self.to_string(with_units=False)
    
    # TODO: add tests for formatting
    def __format__(self, format_spec: str) -> str:
        # Extract type character (if any)
        match = search(r"[a-zA-Z]$", format_spec)
        type_code = match.group() if match else ""
        base_spec = format_spec[:match.start()] if match else format_spec
        
        # Scan all classmethods for one with a matching type code
        for attr in dir(type(self)):
            method = getattr(type(self), attr)
            if (
                callable(method) and hasattr(method, "_format_codes") and
                type_code in method._format_codes
            ):
                return method(self.amount, base_spec)
        raise ValueError(f"Unsupported format type '{type_code}' for {type(self).__name__}")
    
    
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
    
    def to_string(self, *, with_units: bool = False) -> str:
        return format(self, "u" if with_units else "s")
    
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
    
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def _validate_typeless_format(format_spec: str) -> None:
        if search(r"[a-zA-Z]$", format_spec):
            raise ValueError(f"format_spec should not include a type character: '{format_spec}'")
