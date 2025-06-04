"""...

...

"""

from __future__ import annotations

from ...core import EconoModel
from .._instrument import InstrumentMarket
from .base import Loan
from .agents import Lender


__all__ = ["LoanModel", "LoanMarket"]


class LoanModel(EconoModel):
    """...
    
    ...
    """
    
    loan_market: LoanMarket
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.loan_market = LoanMarket(self)


class LoanMarket(InstrumentMarket[Lender, Loan]):
    """A centralized interface for loan coordination between borrowers and lenders."""
    pass
