"""...

...

"""

from __future__ import annotations

from .._instrument.market import InstrumentMarket
from .base import DepositAccount
from .agents import DepositIssuer


__all__ = ["DepositMarket",]


class DepositMarket(InstrumentMarket[DepositIssuer, DepositAccount]):
    """A registry of available deposit accounts.

    Exposes a read-only dict-like interface to model components (e.g. depositors),
    while allowing deposit issuers to register and deregister their products 
    through controlled methods.

    The internal structure maps issuers to a list of deposit account classes.
    """
    pass
