"""...

...

"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....temporal import EconoDate
    from ..._currency import EconoCurrency
    from ..base import Loan
    from ..agents import Borrower


class LoanApplication:
    """...
    
    ...
    """
    
    ##############
    # Attributes #
    ##############
    
    __slots__ = (
        "_loan",
        "_borrower",
        "_principal",
        "_date_opened",
        "_approved",
        "_date_reviewed",
        "_accepted",
        "_date_decided",
        "_date_closed",
    )
    _loan: Loan
    _borrower: Borrower
    _principal: EconoCurrency
    _date_opened: EconoDate
    _date_reviewed: EconoDate
    _approved: bool
    _date_decided: EconoDate
    _accepted: bool
    _date_closed: EconoDate
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(self, 
        loan: Loan,
        borrower: Borrower, 
        principal: EconoCurrency, 
    ) -> None:
        self._loan = loan
        self._borrower = borrower
        self._principal = principal
        self._date_opened = borrower.calendar.today()
        
        self._approved = False
        self._accepted = False
        
        borrower.model.logger.debug(
            f"LoanApplication created on {self.date_opened} by {borrower} for loan {loan}."
        )
    
    ##############
    # Properties #
    ##############
    
    @property
    def loan(self) -> Loan:
        return self._loan
    
    @property
    def borrower(self) -> Borrower:
        return self._borrower
    
    @property
    def principal(self) -> EconoCurrency:
        return self._principal
    
    @property
    def date_opened(self) -> EconoDate:
        return self._date_opened
    
    @property
    def reviewed(self) -> bool:
        return hasattr(self, "_date_reviewed")
    
    @property
    def date_reviewed(self) -> EconoDate:
        if not self.reviewed:
            raise AttributeError(f"{self} has not been reviewed")
        return self._date_reviewed
    
    @property
    def approved(self) -> bool:
        return self._approved
    
    @property
    def denied(self) -> bool:
        return self.reviewed and not self.approved
    
    @property
    def decided(self) -> bool:
        return hasattr(self, "_date_decided")
    
    @property
    def date_decided(self) -> EconoDate:
        if not self.decided:
            raise AttributeError(f"{self} has not been decided")
        return self._date_decided
    
    @property
    def accepted(self) -> bool:
        return self._accepted
    
    @property
    def rejected(self) -> bool:
        return self.decided and not self.accepted
    
    @property
    def closed(self) -> bool:
        return hasattr(self, "_date_closed")
    
    @property
    def date_closed(self) -> EconoDate:
        if not self.closed:
            raise AttributeError(f"{self} is not closed")
        return self._date_closed
    
    
    ###########
    # Methods #
    ###########
    
    def _approve(self, date: EconoDate) -> None:
        if self.reviewed:
            self.borrower.model.logger.debug("LoanApplication is already reviewed: approval attempt ignored.")
            return
        self._approved = True
        self._date_reviewed = date
        self.borrower.model.logger.info(f"LoanApplication approved by {self.loan.lender} on {date}.")
    
    def _deny(self, date: EconoDate) -> None:
        if self.reviewed:
            self.borrower.model.logger.debug("LoanApplication is already reviewed: denial attempt ignored.")
            return
        self._date_reviewed = date
        self.borrower.model.logger.info(f"LoanApplication rejected by {self.loan.lender} on {date}.")
    
    def _accept(self, date: EconoDate) -> Loan | None:
        if self.decided:
            self.borrower.model.logger.warning("LoanApplication is already decided: acceptance attempt ignored.")
            return
        if not self.approved:
            self.borrower.model.logger.warning("LoanApplication is not approved: cannot accept.")
            return
        self._accepted = True
        self._date_decided = date
        self.borrower.model.logger.info(f"LoanApplication accepted by {self.borrower} on {date}.")
        return self.loan.lender._create_debt(self)
    
    def _reject(self, date: EconoDate) -> None:
        if self.decided:
            self.borrower.model.logger.warning("LoanApplication is already decided: rejection attempt ignored.")
            return
        self._date_decided = date
        self.borrower.model.logger.info(f"LoanApplication rejected by {self.borrower} on {date}.")
    
    def _close(self, date: EconoDate) -> None:
        self._date_closed = date