"""...

...

"""

from __future__ import annotations

from typing import Literal, TYPE_CHECKING

from ...core import EconoInstrument
from .interfaces import LoanApplication

if TYPE_CHECKING:
    from ...core import EconoDuration, EconoDate, EconoCurrency
    from .agents import Borrower, Lender
    from .interfaces import LoanRepayment, LoanRepaymentPolicy


__all__ = [
    "Loan",
]


class Loan(EconoInstrument):
    """...
    
    ...
    """
    
    ##############
    # Attributes #
    ##############
    
    # instance attributes
    __slots__ = (
        "_balance",
        "_date_opened",
        "_date_closed",
        "_borrower",
        "_interest_rate",
        "_accrued_interest",
        "repayment_schedule",
    )
    _balance: EconoCurrency
    _date_opened: EconoDate
    _date_closed: EconoDate | None
    _borrower: Borrower
    _interest_rate: float
    _accrued_interest: EconoCurrency
    repayment_schedule: list[LoanRepayment]
    
    # class constants
    __class_constants__ = (
        "lender",
    )
    lender: Lender
    Currency: type[EconoCurrency]
    name: str
    borrower_types: tuple[type[Borrower]]
    limit_per_borrower: int | None
    limit_kind: Literal["outstanding", "cumulative"]
    term: EconoDuration
    disbursement_form: type[EconoInstrument]
    repayment_policy: LoanRepaymentPolicy
    repayment_window: EconoDuration
    repayment_form: type[EconoInstrument]
    relative_interest_rate: bool = False
    
    # class attributes
    minimum_principal: EconoCurrency
    maximum_principal: EconoCurrency
    minimum_interest_rate: float
    maximum_interest_rate: float
    
    
    #################
    # Class Methods #
    #################
    
    @classmethod
    def calculate_interest_rate(cls, instance_rate: float) -> float:
        return cls.minimum_interest_rate + instance_rate
    
    @classmethod
    def is_eligible(cls) -> bool:
        ...
    
    @classmethod
    def apply(cls, applicant: Borrower, principal: EconoCurrency) -> LoanApplication:
        return LoanApplication(
            cls,
            applicant=applicant,
            principal=principal,
            min_principal=cls.minimum_principal,
            min_interest=cls.minimum_interest_rate,
            max_interest=cls.maximum_interest_rate,
            
        )
    
    @classmethod
    def from_application(cls, application: LoanApplication, /) -> Loan | None:
        if application.approved and application.accepted:
            return cls(
                borrower=application.applicant,
                principal=application.principal_offered,
                interest_rate=application.interest_rate_offered,
            )
    
    
    ###################
    # Special Methods #
    ###################

    def __init__(
        self,
        borrower: Borrower,
        principal: EconoCurrency,
        interest_rate: float,
    ) -> None:
        if not isinstance(borrower, Borrower):
            raise TypeError(f"'borrower' ({borrower}) does not inherit from loans.Borrower")
        
        self._borrower = borrower
        self._balance = principal
        self._interest_rate = interest_rate
        self._accrued_interest = self.Currency(0)
        self._date_opened = borrower.calendar.today()
        self._date_closed = None
        self.repayment_schedule = self.repayment_policy(self)
        
        self.lender._register_loan_instance(self)
        self._disburse(amount=self.principal, form=self.disbursement_form)
    
    def __repr__(self) -> str:
        return f"<Loan of {self.principal} from {self.lender} to {self.borrower} on {self.date_opened}>"
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def balance(self) -> EconoCurrency:
        return self._balance
    
    @property
    def date_opened(self) -> EconoDate:
        return self._date_opened
    
    @property
    def date_closed(self) -> EconoDate | None:
        return self._date_closed
    
    @property
    def open(self) -> bool:
        return not self.closed
    
    @property
    def closed(self) -> bool:
        return self.date_closed is not None
    
    @property
    def debtor(self) -> Borrower:
        return self.borrower
    
    @property
    def creditor(self) -> Lender:
        return self.lender
    
    @property
    def borrower(self) -> Borrower:
        return self._borrower
    
    @property
    def principal(self) -> EconoCurrency:
        return self.balance
    
    @property
    def interest_rate(self) -> float:
        if self.relative_interest_rate:
            return self.calculate_interest_rate(self._interest_rate)
        return self._interest_rate
    
    @property
    def accrued_interest(self) -> EconoCurrency:
        return self._accrued_interest
    
    
    ###########
    # Methods #
    ###########
    
    def credit(self, amount: EconoCurrency) -> None:
        self._balance += amount
    
    def debit(self, amount: EconoCurrency) -> None:
        self._balance -= amount
    
    def accrue_interest(self) -> None:
        self._accrued_interest += self.principal * (self.interest_rate / self.lender.calendar.days_per_year())
    
    def capitalize_interest(self) -> None:
        accrued_interest = self.accrued_interest
        self.credit(accrued_interest)
        self._accrued_interest = self.Currency(0)
    
    def repayment_due(self) -> bool:
        return any(payment.due for payment in self.repayment_schedule)
    
    def repayment_amount(self) -> EconoCurrency:
        return sum(
            (
                repayment.amount_due
                for repayment in self.repayment_schedule
                if repayment.due
            ),
            start=self.lender.Currency(0)
        )
    
    def repayments_due(self) -> list[LoanRepayment]:
        return [payment for payment in self.repayment_schedule if payment.due]
    
    def process_repayment(
        self,
        repayment: LoanRepayment,
        /,
        *,
        amount: EconoCurrency | None = None,
        form: type[EconoInstrument] | None = None,
    ) -> None:
        if repayment.due:
            amount = amount if amount is not None else repayment.amount_due
            form = form if form is not None else repayment.form
            self._repay(amount=amount, form=form)
    
    def _disburse(self, amount: EconoCurrency, form: type[EconoInstrument]) -> None:
        self.lender._make_loan_disbursement(self, amount=amount, form=form)
        self.borrower._process_loan_disbursement(self, amount=amount)
        
    def _repay(self, amount: EconoCurrency, form: type[EconoInstrument]) -> None:
        self.borrower._make_loan_repayment(self, amount=amount, form=form)
        self.lender._process_loan_repayment(self, amount=amount)
        self.debit(amount)
