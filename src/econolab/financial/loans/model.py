"""...

...

"""

from __future__ import annotations

from ...core import InstrumentModel, InstrumentMarket
from .base import Loan
from .agents import Borrower, Lender


__all__ = [
    "LoanModel",
    "LoanMarket",
]


class LoanModel(InstrumentModel):
    """...
    
    ...
    """
    
    loan_market: LoanMarket
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.loan_market = LoanMarket(self)


class LoanMarket(InstrumentMarket[Lender, Loan, Borrower]):
    """A centralized interface for loan coordination between borrowers and lenders."""
    pass
