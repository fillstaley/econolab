"""...

...

"""

from __future__ import annotations

from typing import Callable, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from ....temporal import EconoDuration, EconoDate
    from ..._currency import EconoCurrency
    from ..base import Loan


class LoanDisbursement:
    """...
    
    ...
    """
    
    ##############
    # Attributes #
    ##############
    
    __slots__ =(
        "_loan",
        "_amount_due",
        "_date_due",
        "_disbursement_window",
        "_amount_requested",
        "_date_requested",
        "_status",
        "_amount_disbursed",
        "_date_disbursed",
    )
    _loan: Loan
    _amount_due: EconoCurrency
    _date_due: EconoDate
    _disbursement_window: EconoDuration
    _amount_requested: EconoCurrency
    _date_requested: EconoDate
    _status: Literal["pending", "requested", "completed", "expired"]
    _amount_disbursed: EconoCurrency
    _date_disbursed: EconoDate
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self,
        loan: Loan,
        amount_due: EconoCurrency,
        date_due: EconoDate,
        disbursement_window: EconoDuration
    ) -> None:
        self._loan = loan
        self._amount_due = amount_due
        self._date_due = date_due
        self._disbursement_window = disbursement_window
        self._status = "pending"
        
        # for now, we assume all disbursements are requested in full by default
        self._request(self.loan.lender.calendar.today(), amount_due)
    
    def __repr__(self) -> str:
        return f"<LoanDisbursement of {self.amount_due} for {self.loan} due on {self.date_due} ({self.status})>"
    
    def __str__(self) -> str:
        return f"Loan disbursement of {self.amount_due} due on {self.date_due} ({self.status})"
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def loan(self) -> Loan:
        return self._loan
    
    @property
    def amount_due(self) -> EconoCurrency:
        return self._amount_due
    
    @property
    def date_due(self) -> EconoDate:
        return self._date_due
    
    @property
    def disbursement_window(self) -> EconoDuration:
        return self._disbursement_window
    
    @property
    def amount_requested(self) -> EconoCurrency:
        return self._amount_requested
    
    @property
    def date_requested(self) -> EconoDate:
        return self._date_requested
    
    @property
    def amount_disbursed(self) -> EconoCurrency:
        return self._amount_disbursed
    
    @property
    def date_disbursed(self) -> EconoDate:
        return self._date_disbursed
    
    @property
    def status(self) -> str:
        return self._status
    
    @property
    def pending(self) -> bool:
        return self._status == "pending"
    
    @property
    def requested(self) -> bool:
        return self._status == "requested"
    
    @property
    def completed(self) -> bool:
        return self._status == "completed"
    
    @property
    def expired(self) -> bool:
        return self._status == "expired"
    
    @property
    def disbursed(self) -> bool:
        return self._status in {"completed", "expired"}
    
    
    ###########
    # Methods #
    ###########
    
    def is_due(self, date: EconoDate) -> bool:
        return (
            not self.disbursed and
            self.date_due <= date <= self.date_due + self.disbursement_window
        )
    
    def past_due(self, date: EconoDate) -> bool:
        return date >= self.date_due + self.disbursement_window
    
    def _request(self, date: EconoDate, amount: EconoCurrency | None = None) -> bool:
        if self.disbursed:
            self.loan.lender.model.logger.debug(f"LoanDisbursement was disbursed on {self._date_disbursed}: _request() call ignored.")
            return False
        elif self.past_due(date):
            self.loan.lender.model.logger.debug(f"LoanDisbursement was due on {self._date_due}: _request() call ignored.")
            return False
        
        self._status = "requested"
        self._date_requested = date
        self._amount_requested = amount if amount is not None else self.amount_due
        return True
    
    def _complete(self, date: EconoDate) -> bool:
        if self.disbursed:
            self.loan.lender.model.logger.debug(f"LoanDisbursement was disbursed on {self._date_disbursed}: _complete() call ignored.")
            return False
        elif not self.is_due(date):
            self.loan.lender.model.logger.warning(f"Attempted disbursement of {self} outside of payment window.")
            return False
        
        debt = self.loan.lender._disburse_debt(self.amount_requested)
        self.loan.borrower._receive_debt(debt)
        self.loan.repayment_schedule.extend(self.loan.repayment_policy(self))
        
        self._status = "completed"
        self._date_disbursed = date
        self._amount_disbursed = debt
        self.loan.lender.model.logger.info(f"Disbursement for {self.loan} completed on {date}.")
        return True
    
    def _expire(self, date: EconoDate) -> bool:
        if self.disbursed:
            self.loan.lender.model.logger.debug(f"LoanDisbursement was disbursed on {self._date_disbursed}: _expire() call ignored.")
            return False
        elif not self.past_due(date):
            self.loan.lender.model.logger.debug("LoanDisbursement could still be completed: _expire() call ignored.")
            return False
        
        self._status = "expired"
        self._date_disbursed = date
        self._amount_disbursed = self.loan.lender.Currency(0)
        self.loan.lender.model.logger.info(f"Disbursement for {self.loan} expired on {date}.")
        return True


class DisbursementPolicy:
    def __init__(
        self,
        name: str,
        rule: Callable[[Loan], list[LoanDisbursement]]
    ) -> None:
        self._name = name
        self._rule = rule
    
    def __repr__(self) -> str:
        return f"<LoanDisbursementPolicy '{self.name}'>"
    
    def __str__(self) -> str:
        return f"{self.name.capitalize()} loan disbursement policy"
    
    def __call__(self, loan: Loan) -> list[LoanDisbursement]:
        return self._rule(loan)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def name(self) -> str:
        return self._name


def bullet_loan_disbursement_structure(loan: Loan) -> list[LoanDisbursement]:
    return [LoanDisbursement(loan, loan.principal, loan.date_opened, loan.disbursement_window)]

BULLET_DISBURSEMENT = DisbursementPolicy("bullet", rule = bullet_loan_disbursement_structure)

DISBURSEMENT_POLICIES: dict[str, DisbursementPolicy] = {
    "bullet": BULLET_DISBURSEMENT
}