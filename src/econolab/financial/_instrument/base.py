"""A fundamental type for financial assets/liabilities.

...

"""

from abc import abstractmethod
from typing import TYPE_CHECKING

from ...core import EconoProduct, ProductType


__all__ = ["Instrument", "InstrumentType",]


if TYPE_CHECKING:
    from .agents.issuer import Issuer
    from .agents.debtor import Debtor
    from .agents.creditor import Creditor


class InstrumentType(ProductType):
    pass


class Instrument(EconoProduct, metaclass=InstrumentType):
    pass
