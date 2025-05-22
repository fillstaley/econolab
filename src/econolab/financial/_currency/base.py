"""...

...

"""


from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from functools import total_ordering
from re import search
from typing import Callable, cast, Literal, Self, TypeAlias, Union

from ...core.meta import EconoMeta


Numeric: TypeAlias = Union[int, float, str, Decimal]
NUMERIC_TYPES = (int, float, str, Decimal)

Formatter = Callable[[Decimal, str], str]

def register_format_type(*codes):
    def decorator(func):
        func._format_codes = set(codes)
        return func
    return decorator


class CurrencyType(EconoMeta):
    pass

@total_ordering
class EconoCurrency(metaclass=CurrencyType):
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
    
    __constant_attrs__ = {"code"}
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
    
    @classmethod
    @register_format_type("s", "f", "")
    def format_with_symbol(cls, amount: Decimal, format_spec: str = "") -> str:
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
        
        rounded = format(*cls.ensure_precision(amount, format_spec))
        return (
            f"{cls.symbol}{rounded}" if cls.symbol_position == "prefix" else
            f"{rounded} {cls.symbol}"
        )
    
    @classmethod
    @register_format_type("u")
    def format_with_units(cls, amount: Decimal, format_spec: str = "") -> str:
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
        
        rounded = format(*cls.ensure_precision(amount, format_spec))
        unit = (
            cls.unit_name if abs(amount - 1) < 10 ** -cls.precision else
            cls.unit_plural
        )
        return f"{rounded} {unit}"
    
    @classmethod
    def ensure_precision(
        cls,
        amount: Numeric | Self,
        format_spec: str = ""
    ) -> tuple[Decimal, str]:
        """Round amount to the class's precision, respecting format_spec."""
        # If precision is specified in the format string, use it.
        # Otherwise, apply class precision and append it to the format spec.
        if (match := search(r"\.(\d+)", format_spec)):
            precision = int(match[1])
        else:
            precision = cls.precision
            format_spec += f".{precision}"
        # ensure trailing zeros are included
        format_spec += "f"
        
        return cls.convert_to_decimal(amount, precision), format_spec
    
    @classmethod
    def convert_to_decimal(
        cls, 
        amount: Numeric | Self, 
        precision: int | None = None
    ) -> Decimal:
        if isinstance(amount, cls):
            decimal = amount._amount
        elif isinstance(amount, Decimal):
            decimal = amount
        elif isinstance(amount, NUMERIC_TYPES):
            try:
                decimal = Decimal(str(amount))
            except InvalidOperation as e:
                raise InvalidOperation(
                    f"Cannot convert {amount!r} to Decimal; "
                    f"not a valid numeric string or number."
                ) from e
        elif isinstance(amount, EconoCurrency):
            raise TypeError(
                f"Cannot convert instance of {type(amount).__name__} to {cls.__name__}; "
                f"currency types must match for conversion."
            )
        else:
            raise TypeError(
                f"'amount' must be one of these types: {NUMERIC_TYPES} or '{cls.__name__}'; "
                f"got {type(amount).__name__}"
            )
        
        if precision is not None:
            quant = Decimal("1").scaleb(-precision)
            decimal = decimal.quantize(quant, rounding=ROUND_HALF_EVEN)
        return decimal
    
    ###################
    # Special Methods #
    ###################
    
    # TODO: add tests for proper equality relative to precision
    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and (self - other).is_zero()
    
    def __lt__(self, other) -> bool:
        if isinstance(other, type(self)):
            return (self - other).is_negative()
        return NotImplemented
    
    def __hash__(self):
        rounded_amount = self.ensure_precision(self.amount)[0]
        return hash((type(self), rounded_amount))
    
    def __bool__(self) -> bool:
        return bool(self.amount)
    
    def __add__(self, other: Self) -> Self:
        if isinstance(other, type(self)):
            result = self.to_decimal(rounded=False) + other.to_decimal(rounded=False)
            return type(self)(result)
        return NotImplemented
    
    def __sub__(self, other: Self) -> Self:
        if isinstance(other, type(self)):
            result = self.to_decimal(rounded=False) - other.to_decimal(rounded=False)
            return type(self)(result)
        return NotImplemented
    
    def __mul__(self, other: Numeric) -> Self:
        if isinstance(other, NUMERIC_TYPES):
            result = self.to_decimal(rounded=False) * self.convert_to_decimal(other)
            return type(self)(result)
        return NotImplemented
    
    __rmul__ = __mul__
    
    def __truediv__(self, other: Self | Numeric) -> Decimal | Self:
        if isinstance(other, type(self)):
            return self.to_decimal(rounded=False) / other.to_decimal(rounded=False)
        elif isinstance(other, NUMERIC_TYPES):
            result = self.to_decimal(rounded=False) / self.convert_to_decimal(other)
            return type(self)(result)
        return NotImplemented
    
    def __floordiv__(self, other: Self | Numeric) -> Decimal | Self:
        if isinstance(other, type(self)):
            return self.to_decimal(rounded=False) // other.to_decimal(rounded=False)
        elif isinstance(other, NUMERIC_TYPES):
            result = self.to_decimal(rounded=False) // self.convert_to_decimal(other)
            return type(self)(result)
        return NotImplemented
    
    def __mod__(self, other: Self) -> Self:
        if isinstance(other, type(self)):
            result = self.to_decimal(rounded=False) % other.to_decimal(rounded=False)
            return type(self)(result)
        return NotImplemented
    
    def __divmod__(self, other: Self) -> tuple[Decimal, Self]:
        if isinstance(other, type(self)):
            q, r = self // other, self % other
            if not isinstance(q, Decimal):
                raise TypeError(
                    f"Expected quotient to be of type decimal.Decimal; "
                    f"got type '{type(q).__name__}'"
                )
            return q, r
        return NotImplemented
    
    def __neg__(self) -> Self:
        return type(self)(-self.to_decimal(rounded=False))
    
    def __pos__(self) -> Self:
        return type(self)(self.to_decimal(rounded=False))
    
    def __abs__(self) -> Self:
        return type(self)(abs(self.to_decimal(rounded=False)))
    
    def __int__(self) -> int:
        return int(self.to_decimal(rounded=False))
    
    def __float__(self) -> float:
        return float(self.to_decimal(rounded=False))
    
    # TODO: add tests for rounding
    def __round__(self, ndigits: int | None = None) -> Self:
        format_spec = f".{ndigits}" if ndigits is not None else ""
        rounded = self.ensure_precision(self, format_spec)[0]
        return type(self)(rounded)
    
    def __new__(cls, *args, **kwargs):
        if cls is EconoCurrency:
            raise TypeError(
                "EconoCurrency is an abstract base class; "
                "it cannot be instantiated directly.")
        return super().__new__(cls)
    
    # TODO: improve the documentation here
    def __init__(self, amount: Numeric | Self = 0, /) -> None:
        """Initialize a currency instance with a numeric amount.

        Parameters
        ----------
        amount : Numeric or Self, optional
            The numeric value of the currency. Defaults to 0.
        
        Raises
        ------
        InvalidOperation
            If the value cannot be converted to a Decimal.
        
        Examples
        --------
        >>> usd = USD(10.5)
        >>> print(usd)
        $10.50
        """
        try:
            self._amount = self.convert_to_decimal(amount)
        except (InvalidOperation, TypeError) as e:
            raise TypeError(
                f"Invalid amount for {type(self).__name__} initialization: "
                f"{amount!r} cannot be converted to Decimal."
            ) from e
    
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.to_decimal(rounded=False)!r})"
    
    def __str__(self) -> str:
        return format(self, "")
    
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
                callable(method) and type_code in getattr(method, "_format_codes", [])
            ):
                typed_method = cast(Formatter, method)
                return typed_method(self.amount, base_spec)
        raise ValueError(f"Unsupported format type '{type_code}' for {type(self).__name__}")
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def amount(self) -> Decimal:
        """The amount of currency."""
        return self._amount
    
    @amount.setter
    def amount(self, _: float) -> None:
        raise AttributeError("readonly attribute")
    
    
    ###########
    # Methods #
    ###########
    
    def to_decimal(self, *, rounded: bool = True) -> Decimal:
        return self.convert_to_decimal(self, self.precision if rounded else None)
    
    def to_string(self, *, with_units: bool = False) -> str:
        return format(self, "u" if with_units else "s")
    
    # TODO: add tests for these comparison methods
    def is_zero(self) -> bool:
        """Return True if the currency amount is zero, relative to its precision."""
        return self.is_positive_or_zero() and self.is_negative_or_zero()
    
    def is_positive(self) -> bool:
        """Return True if the currency amount is greater than zero.
        
        Uses the currency's precision to compare against a small positive number.
        """
        return not self.is_negative_or_zero()
    
    def is_negative(self) -> bool:
        """Return True if the currency amount is less than zero.
        
        Uses the currency's precision to compare against a small negative number.
        """
        return not self.is_positive_or_zero()

    def is_positive_or_zero(self) -> bool:
        """Return True if the currency amount is greater than or equal to zero.
        
        Uses the currency's precision to compare against a small negative number.
        """
        return self.to_decimal() > -Decimal("1").scaleb(-self.precision)

    def is_negative_or_zero(self) -> bool:
        """Return True if the currency amount is less than or equal to zero.
        
        Uses the currency's precision to compare against a small positive number.
        """
        return self.to_decimal() < Decimal("1").scaleb(-self.precision)
    
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def _validate_typeless_format(format_spec: str) -> None:
        if search(r"[a-zA-Z]$", format_spec):
            raise ValueError(
                f"format_spec should not include a type character: '{format_spec}'"
            )
