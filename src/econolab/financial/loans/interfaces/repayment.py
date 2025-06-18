"""...

...

"""

from __future__ import annotations

from typing import Callable, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from ....temporal import EconoDuration, EconoDate
    from ....financial import EconoCurrency
    from ..._instrument import Instrument
    from ..base import Loan
    from ..agents import Borrower, Lender


class LoanRepayment:
    """...
    
    ...
    """
    
    ##############
    # Attributes #
    ##############
    
    __slots__ = (
        "_loan",
        "_amount_due",
        "_date_due",
        "_repayment_window",
        "_repayment_form",
        "_date_opened",
        "_date_closed",
        "_amount_paid",
        "_date_paid",
    )
    _loan: Loan
    _amount_due: EconoCurrency
    _date_due: EconoDate
    _repayment_window: EconoDuration
    _repayment_form: type[Instrument]
    _date_opened: EconoDate
    _date_closed: EconoDate | None
    _amount_paid: EconoCurrency | None
    _date_paid: EconoDate | None
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self,
        loan: Loan,
        amount_due: EconoCurrency, 
        date_due: EconoDate, 
        repayment_window: EconoDuration,
        repayment_form: type[Instrument],
    ) -> None:
        self._loan = loan
        self._amount_due = amount_due
        self._date_due = date_due
        self._repayment_window = repayment_window
        self._repayment_form = repayment_form
        self._date_opened = self.borrower.calendar.today()
        self._date_closed = None
        self._amount_paid = None
        self._date_paid = None
    
    def __repr__(self) -> str:
        status = "paid" if self.paid else "unpaid"
        return f"<LoanPayment of {self.amount_due} for {self.loan} due on {self.date_due} ({status}).>"
    
    def __str__(self) -> str:
        status = "Paid" if self.paid else "Unpaid"
        return f"Loan payment of {self.amount_due} due on {self.date_due} ({status})"
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def loan(self) -> Loan:
        return self._loan
    
    @property
    def lender(self) -> Lender:
        return self.loan.lender
    
    @property
    def borrower(self) -> Borrower:
        return self.loan.borrower
    
    @property
    def amount_due(self) -> EconoCurrency:
        return self._amount_due
    
    @property
    def date_due(self) -> EconoDate:
        return self._date_due
    
    @property
    def due(self) -> bool:
        repayment_date = cast(EconoDate, self.date_due - self.repayment_window)
        return (
            not self.paid
            and self.borrower.calendar.today() >= repayment_date
        )
    
    @property
    def overdue(self) -> bool:
        return not self.paid and self.borrower.calendar.today() > self.date_due
    
    @property
    def repayment_window(self) -> EconoDuration:
        return self._repayment_window
    
    @property
    def repayment_form(self) -> type[Instrument]:
        return self._repayment_form
    
    @property
    def open(self) -> bool:
        return not self.closed
    
    @property
    def date_opened(self) -> EconoDate:
        return self._date_opened
    
    @property
    def closed(self) -> bool:
        return self._date_closed is not None
    
    @property
    def date_closed(self) -> EconoDate | None:
        return self._date_closed
    
    @property
    def paid(self) -> bool:
        return self._date_paid is not None
    
    @property
    def amount_paid(self) -> EconoCurrency | None:
        return self._amount_paid
    
    @property
    def date_paid(self) -> EconoDate | None:
        return self._date_paid
    
    
    ###########
    # Methods #
    ###########
    
    def _close(self) -> None:
        if not self.closed:
            self._date_closed = self.borrower.calendar.today()
    
    def _complete(self) -> None:
        if not self.closed and self.due:
            self.loan.process_repayment(self)
            self._close()
    
    def _default(self) -> None:
        if not self.closed:
            self._close()


class RepaymentPolicy:
    def __init__(
        self,
        name: str,
        rule: Callable[[Loan], list[LoanRepayment]]
    ) -> None:
        self._name = name
        self._rule = rule
    
    def __repr__(self) -> str:
        return f"<LoanPaymentStructure '{self.name}'>"
    
    def __str__(self) -> str:
        return f"{self.name.capitalize()} loan payment structure"
    
    def __call__(self, loan: Loan) -> list[LoanRepayment]:
        return self._rule(loan)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def name(self) -> str:
        return self._name


def bullet_loan_repayment_policy(loan: Loan) -> list[LoanRepayment]:
    return [
        LoanRepayment(
            loan,
            loan.balance,
            loan.date_opened + loan.term,
            loan.repayment_window,
            loan.repayment_form
        )
    ]

BULLET_REPAYMENT = RepaymentPolicy("bullet", rule = bullet_loan_repayment_policy)

REPAYMENT_POLICIES = {
        "bullet": BULLET_REPAYMENT
}
