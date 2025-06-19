"""A fundamental type for financial assets/liabilities.

...

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...core import EconoProduct, ProductType

if TYPE_CHECKING:
    from ..currency import EconoCurrency
    from .agents import EconoIssuer


__all__ = [
    "EconoInstrument",
    "InstrumentType",
]


class InstrumentType(ProductType):
    pass


class EconoInstrument(EconoProduct, metaclass=InstrumentType):
    issuer: EconoIssuer
    Currency: type[EconoCurrency]
