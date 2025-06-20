"""...

...

"""

from __future__ import annotations

from typing import cast, TYPE_CHECKING

from ....core import EconoApplication

if TYPE_CHECKING:
    from ....core import EconoCurrency
    from ..base import Loan
    from ..agents import Borrower, Lender


__all__ = [
    "LoanApplication",
]


class LoanApplication(EconoApplication):
    """...
    
    LoanApplication represents a borrower's request for a loan,
    capturing both the initial intent and the lender's response.
    An application progresses through the following states:

    - opened → reviewed → approved/denied → accepted/rejected → closed
    """
    
    ##############
    # Attributes #
    ##############
    
    __slots__ = (
        "_loan_class",
        "_principal_requested",
        "_minimum_principal",
        "_minimum_interest_rate",
        "_maximum_interest_rate",
        "_principal_offered",
        "_interest_rate_offered",
    )
    _loan_class: type[Loan]
    _principal_requested: EconoCurrency
    _minimum_principal: EconoCurrency
    _minimum_interest_rate: float
    _maximum_interest_rate: float
    _principal_offered: EconoCurrency
    _interest_rate_offered: float
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(self, 
        loan: type[Loan],
        /,
        applicant: Borrower,
        principal: EconoCurrency,
        min_principal: EconoCurrency,
        min_interest: float,
        max_interest: float,
    ) -> None:
        super().__init__(applicant=applicant)
        
        self._loan_class = loan
        self._principal_requested = principal
        self._minimum_principal = min_principal
        self._minimum_interest_rate = min_interest
        self._maximum_interest_rate = max_interest
        self._principal_offered = self.Loan.Currency(0)
        self._interest_rate_offered = 0.0
        
        self.lender._register_loan_application(self)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def Loan(self) -> type[Loan]:
        return self._loan_class
    
    @property
    def lender(self) -> Lender:
        return self.Loan.lender
    
    @property
    def applicant(self) -> Borrower:
        return cast(Borrower, self._applicant)
    
    @property
    def principal_requested(self) -> EconoCurrency:
        return self._principal_requested
    
    @property
    def minimum_principal(self) -> EconoCurrency:
        return self._minimum_principal
    
    @property
    def minimum_interest_rate(self) -> float:
        return self._minimum_interest_rate
    
    @property
    def maximum_interest_rate(self) -> float:
        return self._maximum_interest_rate
    
    @property
    def principal_offered(self) -> EconoCurrency:
        return self._principal_offered
    
    @property
    def interest_rate_offered(self) -> float:
        return self._interest_rate_offered
    
    
    ###########
    # Methods #
    ###########
    
    def approve(self, amount: EconoCurrency, rate: float) -> bool:
        if not self.reviewed:
            self._approved = True
            self._principal_offered = amount
            self._interest_rate_offered = rate
            self._review()
            return True
        return False
    
    def deny(self) -> bool:
        if not self.reviewed:
            self._review()
            self._close()
            return True
        return False
    
    def accept(self) -> Loan | None:
        if not self.closed and self.approved:
            self._accepted = True
            loan = self.Loan.from_application(self)
            self._close()
            return loan
        return None
    
    def reject(self) -> bool:
        if not self.closed:
            self._close()
            return True
        return False
