"""...

...

"""

from __future__ import annotations

from ..agent import EconoAgent, EconoModelLike


__all__ = [
    "InstrumentModelLike",
    "Issuer",
    "Debtor",
    "Creditor",
]


class InstrumentModelLike(EconoModelLike):
    pass


class Issuer(EconoAgent):
    pass


class Debtor(EconoAgent):
    pass


class Creditor(EconoAgent):
    pass
