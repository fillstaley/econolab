"""A fundamental type for financial assets/liabilities.

...

"""

from __future__ import annotations

from ...core import EconoProduct, ProductType


__all__ = [
    "EconoInstrument",
    "InstrumentType",
]


class InstrumentType(ProductType):
    pass


class EconoInstrument(EconoProduct, metaclass=InstrumentType):
    pass
