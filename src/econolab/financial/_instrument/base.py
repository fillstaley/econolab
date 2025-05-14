"""A fundamental type for financial assets/liabilities.

...

"""

from typing import TYPE_CHECKING

from ...core import EconoMeta


if TYPE_CHECKING:
    from .agents.issuer import Issuer
    from .agents.debtor import Debtor
    from .agents.creditor import Creditor


class InstrumentType(EconoMeta):
    pass


class Instrument(metaclass=InstrumentType):
    issuer: Issuer
    Debtor: Debtor
    Creditor: Creditor
