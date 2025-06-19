"""...

...

"""

from __future__ import annotations

from typing import cast, TYPE_CHECKING

if TYPE_CHECKING:
    from ....core import EconoAgent, EconoCurrency
    from ....temporal import EconoDate
    from ..base import Loan
    from ..agents import Borrower, Lender


__all__ = [
    "LoanApplication",
]


class Application:
    __slots__ = (
        "_applicant",
        "_date_opened",
        "_date_reviewed",
        "_date_closed",
        "_approved",
        "_accepted",
    )
    _applicant: EconoAgent
    _date_opened: EconoDate
    _date_reviewed: EconoDate | None
    _date_closed: EconoDate | None
    _approved: bool
    _accepted: bool
    
    
    def __init__(
        self,
        applicant: EconoAgent,
    ) -> None:
        self._applicant = applicant
        
        self._date_opened = applicant.calendar.today()
        self._date_reviewed = None
        self._date_closed = None
        self._approved = False
        self._accepted = False
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def applicant(self) -> EconoAgent:
        return self._applicant
    
    @property
    def date_opened(self) -> EconoDate:
        return self._date_opened
    
    @property
    def date_reviewed(self) -> EconoDate | None:
        return self._date_reviewed
    
    @property
    def date_closed(self) -> EconoDate | None:
        return self._date_closed
    
    
    ##########
    # States #
    ##########
    
    @property
    def open(self) -> bool:
        return not self.closed
    
    @property
    def reviewed(self) -> bool:
        return self.date_reviewed is not None
    
    @property
    def closed(self) -> bool:
        return self.date_closed is not None
    
    @property
    def approved(self) -> bool:
        return self.reviewed and self._approved
    
    @property
    def denied(self) -> bool:
        return self.reviewed and not self.approved
    
    @property
    def accepted(self) -> bool:
        return self.closed and self._accepted
    
    @property
    def rejected(self) -> bool:
        return self.closed and not self.accepted
    
    
    ###########
    # Methods #
    ###########
    
    def _review(self) -> bool:
        if not self.reviewed:
            self._date_reviewed = self.applicant.calendar.today()
            return True
        return False
    
    def _close(self) -> bool:
        if not self.closed:
            self._date_closed = self.applicant.calendar.today()
            return True
        return False


class LoanApplication(Application):
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
