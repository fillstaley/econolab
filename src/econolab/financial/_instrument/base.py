"""A fundamental type for financial assets/liabilities.

...

"""

from abc import abstractmethod
from typing import TYPE_CHECKING

from ...core import EconoMeta


if TYPE_CHECKING:
    from .agents.issuer import Issuer
    from .agents.debtor import Debtor
    from .agents.creditor import Creditor


class InstrumentType(EconoMeta):
    pass


class Instrument(metaclass=InstrumentType):
    
    @property
    @abstractmethod
    def issuer(self) -> Issuer:
        pass
    
    @property
    @abstractmethod
    def debtor(self) -> Debtor:
        pass
    
    @property
    @abstractmethod
    def creditor(self) -> Creditor:
        pass
