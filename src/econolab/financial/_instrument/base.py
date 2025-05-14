"""A fundamental type for financial assets/liabilities.

...

"""

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .agents.issuer import Issuer
    from .agents.debtor import Debtor
    from .agents.creditor import Creditor


class InstrumentType(type):
    pass


class Instrument(metaclass=InstrumentType):
    issuer: Issuer
    Debtor: Debtor
    Creditor: Creditor
