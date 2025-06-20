"""Defines an abstract base class for monetary value in EconoLab models.

...

"""

from .base import EconoCurrency, CurrencyType
from .spec import CurrencySpecification


__all__ = [
    "EconoCurrency",
    "CurrencyType",
    "CurrencySpecification",
]
