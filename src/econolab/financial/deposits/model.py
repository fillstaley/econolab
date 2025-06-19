"""...

...

"""

from __future__ import annotations

from ...core import EconoModel, InstrumentMarket
from .base import DepositAccount
from .agents import Depositor, DepositIssuer


__all__ = [
    "DepositModel",
    "DepositMarket",
]


class DepositModel(EconoModel):
    """...
    
    ...
    """
    
    deposit_market: DepositMarket
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.deposit_market = DepositMarket(self)


class DepositMarket(InstrumentMarket[DepositIssuer, DepositAccount, Depositor]):
    """A registry of available deposit accounts.

    Exposes a read-only dict-like interface to model components (e.g. depositors),
    while allowing deposit issuers to register and deregister their products 
    through controlled methods.

    The internal structure maps issuers to a list of deposit account classes.
    """
    pass
