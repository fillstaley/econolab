"""Credit base class for representing monetary quantities.

This module defines the `Credit` class, a lightweight, immutable representation 
of a monetary quantity used throughout the EconoLab framework. Credit instances 
support arithmetic, comparison, rounding, and formatting operations, and are 
associated with an optional `Currency`.

This class is designed to be the atomic unit of monetary credit issued, held, 
transferred, and redeemed by agents in financial simulations.

"""

from __future__ import annotations
from functools import total_ordering

from ..currency import Currency


@total_ordering
class Credit:
    """Represents a quantity of credit as a monetary object.

    Credit instances behave like scalar values representing an amount of 
    monetary credit. They support arithmetic, comparison, and rounding 
    operations, and are designed to be lightweight, immutable containers 
    for representing money in circulation within a model.

    This class is the atomic unit of credit issued and redeemed by lenders, 
    held by borrowers, and used as the basis for financial transactions. 
    It supports optional currency metadata to track units of account and 
    precision.
    
    Parameters
    ----------
    amount : int | float, optional
        The numeric value representing the amount of credit, defaults to 0.
    currency : Currency | None, optional
        The currency associated with the credit, defaults to None.
    
    """
    
    __slots__ = ("_amount", "_currency")
    
    DEFAULT_PRECISION = Currency.DEFAULT_PRECISION  # Default precision for rounding
    
    #################
    # Class Methods #
    #################
    
    @classmethod
    def from_dict(cls, data: dict) -> Credit:
        return cls(data["amount"], Currency.from_dict(data["currency"]))
    
    
    ###########
    # Methods #
    ###########
    
    def _assert_compatible(self, other: Credit) -> None:
        """Raise ValueError if the currencies of two Credit objects are incompatible."""
        if self.currency != other.currency:
            raise ValueError("Cannot operate on Credit with different currencies.")
    
    
    ###################
    # Special Methods #
    ###################

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Credit):
            return False if self.currency != other.currency else (self - other).is_zero()
        elif isinstance(other, int | float):
            return self.amount == other
        return NotImplemented
    
    def __lt__(self, other: object) -> bool:
        if isinstance(other, Credit):
            self._assert_compatible(other)
            return self.amount < other.amount
        elif isinstance(other, int | float):
            return self.amount < other
        return NotImplemented
    
    def __hash__(self) -> int:
        return hash((round(self.amount, self.precision), self.currency))
    
    def __bool__(self) -> bool:
        return bool(self.amount)
    
    def __add__(self, other: Credit) -> Credit:
        if isinstance(other, Credit):
            self._assert_compatible(other)
            return Credit(self.amount + other.amount, self.currency)
        return NotImplemented
    
    def __sub__(self, other: Credit) -> Credit:
        if isinstance(other, Credit):
            self._assert_compatible(other)
            return Credit(self.amount - other.amount, self.currency)
        return NotImplemented
    
    def __mul__(self, other: int | float) -> Credit:
        if isinstance(other, int | float):
            return Credit(self.amount * other, self.currency)
        return NotImplemented
    
    __rmul__ = __mul__

    def __truediv__(self, other: Credit | int | float) -> float | Credit:
        if isinstance(other, Credit):
            if other.amount == 0:
                raise ZeroDivisionError("Division by zero-valued Credit")
            self._assert_compatible(other)
            return self.amount / other.amount
        elif isinstance(other, int | float):
            if other == 0:
                raise ZeroDivisionError("Division by zero")
            return Credit(self.amount / other, self.currency)
        return NotImplemented
    
    def __floordiv__(self, other: Credit | int) -> int | Credit:
        if isinstance(other, Credit):
            if other.amount == 0:
                raise ZeroDivisionError("Division by zero-valued Credit")
            self._assert_compatible(other)
            return self.amount // other.amount
        return NotImplemented
    
    def __mod__(self, other: Credit) -> Credit:
        if isinstance(other, Credit):
            if other.amount == 0:
                raise ZeroDivisionError("Division by zero-valued Credit")
            self._assert_compatible(other)
            return Credit(self.amount % other.amount, self.currency)
        return NotImplemented
    
    def __divmod__(self, other: Credit) -> tuple[int, Credit]:
        if isinstance(other, Credit):
            self._assert_compatible(other)
            return self // other, self % other
        return NotImplemented

    def __neg__(self) -> Credit:
        return Credit(-self.amount, self.currency)
    
    def __pos__(self) -> Credit:
        return self

    def __abs__(self) -> Credit:
        return Credit(abs(self.amount), self.currency)
    
    def __int__(self) -> int:
        return int(self.amount)

    def __float__(self) -> float:
        return round(self.amount, self.precision)
    
    def __round__(self, ndigits: int | None = None) -> float:
        return round(self.amount, ndigits if ndigits is not None else self.precision)

    def __init__(self, amount: int | float = 0, currency: Currency | None = None) -> None:
        self._amount = float(amount)
        self._currency = currency

    def __repr__(self) -> str:
        return f"Credit({self.amount}, currency={repr(self.currency)})"

    def __str__(self) -> str:
        if self.currency:
            return self.currency(self.amount)
        return f"{self.amount:.{self.precision}f}"
    
    def __format__(self, format_spec: str) -> str:
        # Default: defer to string if no format_spec
        if not format_spec:
            return str(self)

        # Format using currency, if defined
        if self.currency:
            return self.currency(self.amount, format_spec)
        return format(self.amount, format_spec)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @property
    def currency(self) -> Currency | None:
        return self._currency

    @property
    def precision(self) -> int:
        return self.currency.precision if self.currency else self.DEFAULT_PRECISION
    
    
    ###########
    # Methods #
    ###########
    
    def is_zero(self) -> bool:
        """Return True if the credit amount is approximately zero, based on precision."""
        return not self.is_positive() and not self.is_negative()
    
    def is_positive(self) -> bool:
        """Return True if the credit amount is greater than zero, using the defined precision."""
        return self.amount > 10 ** -self.precision
    
    def is_negative(self) -> bool:
        """Return True if the credit amount is less than zero, using the defined precision."""
        return self.amount < -10 ** -self.precision

    def is_positive_or_zero(self) -> bool:
        """Return True if the credit amount is greater than or equal to zero, using the defined precision."""
        return self.amount > -10 ** -self.precision

    def is_negative_or_zero(self) -> bool:
        """Return True if the credit amount is less than or equal to zero, using the defined precision."""
        return self.amount < 10 ** -self.precision
    
    def to_dict(self) -> dict:
        return {"amount": self.amount, "currency": self.currency.to_dict()}
