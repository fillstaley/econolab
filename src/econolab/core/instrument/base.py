"""A fundamental type for financial assets/liabilities.

...

"""

from __future__ import annotations

from ...core import EconoProduct, ProductType


__all__ = ["Instrument", "InstrumentType",]


class InstrumentType(ProductType):
    pass


class Instrument(EconoProduct, metaclass=InstrumentType):
    pass
