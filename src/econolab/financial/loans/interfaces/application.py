"""...

...

"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....temporal import EconoDate
    from ..._currency import EconoCurrency
    from ..base import Loan
    from ..agents import Borrower, Lender


class LoanApplication:
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
        "_applicant",
        "_date_opened",
        "_date_reviewed",
        "_date_closed",
        "_accepted",
        "_loan_class",
        "_principal_requested",
        "_minimum_principal",
        "_minimum_interest_rate",
        "_maximum_interest_rate",
        "_principal_offered",
        "_interest_rate_offered",
    )
    _applicant: Borrower
    _date_opened: EconoDate
    _date_reviewed: EconoDate | None
    _date_closed: EconoDate | None
    _accepted: bool
    
    _loan_class: type[Loan]
    _principal_requested: EconoCurrency
    _minimum_principal: EconoCurrency
    _minimum_interest_rate: float
    _maximum_interest_rate: float
    _principal_offered: EconoCurrency | None
    _interest_rate_offered: float | None
    
    
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
        self._applicant = applicant
        self._date_opened = applicant.calendar.today()
        self._date_reviewed = None
        self._date_closed = None
        self._accepted = False
        
        self._loan_class = loan
        self._principal_requested = principal
        self._minimum_principal = min_principal
        self._minimum_interest_rate = min_interest
        self._maximum_interest_rate = max_interest
        self._principal_offered = None
        self._interest_rate_offered = None
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def applicant(self) -> Borrower:
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
    
    @property
    def opened(self) -> bool:
        return self.date_closed is None
    
    @property
    def reviewed(self) -> bool:
        return self.date_reviewed is not None
    
    @property
    def closed(self) -> bool:
        return self.date_closed is not None
    
    @property
    def accepted(self) -> bool:
        return self.closed and self._accepted
    
    @property
    def rejected(self) -> bool:
        return self.closed and not self.accepted
    
    @property
    def loan(self) -> type[Loan]:
        return self._loan_class
    
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
    def principal_offered(self) -> EconoCurrency | None:
        return self._principal_offered
    
    @property
    def interest_rate_offered(self) -> float | None:
        return self._interest_rate_offered
    
    @property
    def approved(self) -> bool:
        return self.reviewed and bool(self.principal_offered)
    
    @property
    def denied(self) -> bool:
        return self.reviewed and not self.approved
    
    
    ###########
    # Methods #
    ###########
    
    def _close(self) -> None:
        if not self.closed:
            self._date_closed = self.applicant.calendar.today()
    
    def _approve(self, lender: Lender, amount: EconoCurrency, rate: float) -> None:
        if self.reviewed:
            lender.model.logger.warning(
                "LoanApplication is already reviewed: approval attempt ignored."
            )
        else:
            self._date_reviewed = lender.calendar.today()
            self._principal_offered = amount
            self._interest_rate_offered = rate
            lender.model.logger.debug(
                "LoanApplication approved by %s on %s.", lender, self.date_reviewed
            )
    
    def _deny(self, lender: Lender) -> None:
        if self.reviewed:
            lender.model.logger.warning(
                "LoanApplication is already reviewed: denial attempt ignored."
            )
        else:
            self._date_reviewed = lender.calendar.today()
            self._close()
            lender.model.logger.debug(
                "LoanApplication rejected by %s on %s.", lender, self.date_reviewed
            )
    
    def _accept(self, applicant: Borrower) -> Loan | None:
        if self.closed:
            applicant.model.logger.warning(
                "LoanApplication is already closed: acceptance attempt ignored."
            )
        elif not self.approved:
            applicant.model.logger.warning(
                "LoanApplication is not approved: cannot accept."
            )
        else:
            self._close()
            self._accepted = True
            applicant.model.logger.debug(
                "LoanApplication accepted by %s on %s.", applicant, self.date_closed
            )
            return self.loan.lender._create_debt(self)
    
    def _reject(self, applicant: Borrower) -> None:
        if self.closed:
            applicant.model.logger.warning(
                "LoanApplication is already closed: rejection attempt ignored."
            )
        else:
            self._close()
            applicant.model.logger.info(
                "LoanApplication rejected by %s on %s.", applicant, self.date_closed
            )
