"""...

...

"""

from __future__ import annotations

from typing import Callable, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from ....core import EconoAgent, EconoCurrency
    from ....temporal import EconoDuration, EconoDate
    from ..._instrument import Instrument
    from ..base import Loan
    from ..agents import Borrower, Lender


__all__ = [
    "LoanRepayment",
    "LoanRepaymentPolicy",
    "LOAN_REPAYMENT_POLICIES",
]


class Payment:
    __slots__ = (
        "_payer",
        "_recipient",
        "_amount_due",
        "_form",
        "_date_due",
        "_window",
        "_date_opened",
        "_date_closed",
        "_amount_paid",
    )
    _payer: EconoAgent
    _recipient: EconoAgent
    _amount_due: EconoCurrency
    _form: type[Instrument]
    _date_due: EconoDate
    _window: EconoDuration
    _date_opened: EconoDate
    _date_closed: EconoDate | None
    _amount_paid: EconoCurrency | None
    
    
    def __init__(
        self,
        payer: EconoAgent,
        recipient: EconoAgent,
        amount: EconoCurrency,
        form: type[Instrument],
        date: EconoDate,
        window: EconoDuration,
    ) -> None:
        self._payer = payer
        self._recipient = recipient
        self._amount_due = amount
        self._form = form
        self._date_due = date
        self._window = window
        self._date_opened = payer.calendar.today()
        
        self._date_closed = None
        self._amount_paid = None
    
    def __repr__(self) -> str:
        status = "paid" if self.completed else "unpaid"
        return (
            f"<{type(self).__name__} from {self.payer} to {self.recipient}"
            f" of {self.amount_due} due on {self.date_due} ({status})"
        )
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def payer(self) -> EconoAgent:
        return self._payer
    
    @property
    def recipient(self) -> EconoAgent:
        return self._recipient
    
    @property
    def amount_due(self) -> EconoCurrency:
        return self._amount_due
    
    @property
    def form(self) -> type[Instrument]:
        return self._form
    
    @property
    def date_due(self) -> EconoDate:
        return self._date_due
    
    @property
    def window(self) -> EconoDuration:
        return self._window
    
    @property
    def date_opened(self) -> EconoDate:
        return self._date_opened
    
    @property
    def date_closed(self) -> EconoDate | None:
        return self._date_closed
    
    @property
    def amount_paid(self) -> EconoCurrency | None:
        return self._amount_paid
    
    
    ##########
    # States #
    ##########
    
    @property
    def open(self) -> bool:
        return not self.closed
    
    @property
    def closed(self) -> bool:
        return self.date_closed is not None
    
    @property
    def due(self) -> bool:
        today = self.payer.calendar.today()
        earliest_date = cast(EconoDate, self.date_due - self.window)
        return self.open and today >= earliest_date
    
    @property
    def overdue(self) -> bool:
        today = self.payer.calendar.today()
        return self.open and today > self.date_due
    
    @property
    def completed(self) -> bool:
        return self.closed and self.amount_paid == self.amount_due
    
    @property
    def defaulted(self) -> bool:
        return self.closed and not self.amount_paid
    
    
    ###########
    # Methods #
    ###########
    
    def _close(self) -> None:
        if not self.closed:
            self._date_closed = self.payer.calendar.today()
    
    def complete(self) -> bool:
        if not self.closed and self.due:
            self._amount_paid = self._amount_due
            self._close()
            return True
        return False
    
    def default(self) -> bool:
        if not self.closed and self.due:
            self._amount_paid = self.payer.Currency(0)
            self._close()
            return True
        return False


class LoanRepayment(Payment):
    """...
    
    ...
    """
    
    ##############
    # Attributes #
    ##############
    
    __slots__ = (
        "_loan",
    )
    _loan: Loan
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self,
        loan: Loan,
        /,
        amount: EconoCurrency, 
        form: type[Instrument],
        date: EconoDate, 
        window: EconoDuration,
    ) -> None:
        super().__init__(
            payer=loan.borrower,
            recipient=loan.lender,
            amount=amount,
            form=form,
            date=date,
            window=window,
        )
        self._loan = loan
    
    
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
    
    
    ###########
    # Methods #
    ###########
    
    def complete(self) -> bool:
        if self.due:
            self.loan.process_repayment(self)
            super().complete()
            return True
        return False
    
    def default(self) -> bool:
        if self.due:
            super().default()
            return True
        return False


class LoanRepaymentPolicy:
    def __init__(
        self,
        name: str,
        rule: Callable[[Loan], list[LoanRepayment]]
    ) -> None:
        self._name = name
        self._rule = rule
    
    def __call__(self, loan: Loan) -> list[LoanRepayment]:
        return self._rule(loan)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def name(self) -> str:
        return self._name


def bullet_repayment_rule(loan: Loan) -> list[LoanRepayment]:
    return [
        LoanRepayment(
            loan,
            amount=loan.balance,
            form=loan.repayment_form,
            date=loan.date_opened + loan.term,
            window=loan.repayment_window,
        )
    ]

BULLET_REPAYMENT = LoanRepaymentPolicy("bullet", rule=bullet_repayment_rule)

LOAN_REPAYMENT_POLICIES = {
        "bullet": BULLET_REPAYMENT
}
