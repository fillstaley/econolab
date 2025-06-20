"""...

...

"""

from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from ....core import EconoPayment

if TYPE_CHECKING:
    from ....core import EconoCurrency, EconoDuration, EconoDate, EconoInstrument
    from ..base import Loan
    from ..agents import Borrower, Lender


__all__ = [
    "LoanRepayment",
    "LoanRepaymentPolicy",
    "LOAN_REPAYMENT_POLICIES",
]


class LoanRepayment(EconoPayment):
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
        form: type[EconoInstrument],
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
