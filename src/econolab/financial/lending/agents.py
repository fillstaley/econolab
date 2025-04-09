"""...

...

"""


from __future__ import annotations

import logging
logger = logging.getLogger(__name__)

from collections import defaultdict, deque
from typing import TYPE_CHECKING

from ...core import BaseAgent
from ..credit import Credit

if TYPE_CHECKING:
    from .loan import Loan, LoanDisbursement, LoanPayment, LoanOption, LoanApplication


class InsufficientCreditError(Exception):
    pass

class Borrower(BaseAgent):
    def __init__(self, *args, debt_limit: int | float | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        # initialize agent counters
        self.counters.add_counters(
            "loans_incurred",
            type_ = int
        )
        
        self.counters.add_counters(
            "debt_incurred",
            "debt_received",
            "debt_repaid",
            "credit_taken",
            "credit_given",
            type_ = Credit
        )
        
        if debt_limit is not None and (not isinstance(debt_limit, int | float) or debt_limit < 0):
            raise ValueError(f"'debt_limit' must be nonnegative or 'None', got {debt_limit}.")
        self.debt_limit = debt_limit if debt_limit is not None else float("inf")
        
        self._open_loan_applications: list[LoanApplication] = []
        self._closed_loan_applications: list[LoanApplication] = []
        
        self._loans: list[Loan] = []
        
        self.credit: Credit = Credit(0)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def reviewed_loan_applications(self) -> list[LoanApplication]:
        return [loan for loan in self._open_loan_applications if loan.date_reviewed]
    
    @property
    def debt_load(self) -> float:
        return sum(loan.principal for loan in self._loans) if self._loans else 0
    
    @property
    def debt_capacity(self) -> float | bool:
        return max(0, self.debt_limit - self.debt_load) if self.debt_limit is not None else True
    
    @property
    def outstanding_debt(self) -> float:
        return sum(l.principal for l in self._loans)
    
    
    ###########
    # Methods #
    ###########
    
    def take_credit(self, credit: Credit) -> None:
        """Receive a quantity of credit and add it to the wallet. Increments `credit_taken`."""
        if not isinstance(credit, Credit):
            raise ValueError(f"'credit' should be an instance of Credit; got {type(credit).__name__}.")
        self.credit += credit
        self.counters.increment("credit_taken", credit)
    
    def give_credit(self, amount: float) -> Credit | None:
        """Removes credit from this agent and returns it, raising an error if insufficient."""
        if amount <= 0:
            raise ValueError("'credit' must be positive.")
        if self.credit < amount:
            raise InsufficientCreditError(f"{self} has only {self.credit}, cannot give {amount}.")
        credit = Credit(amount)
        self.credit -= credit
        self.counters.increment("credit_given", credit)
        return credit
    
    def incur_debt(self, loan_application: LoanApplication) -> None:
        today = self.calendar.today()
        loan = loan_application.accept(today)
        self._loans.append(loan)
        self.counters.increment("loans_incurred")
        self.counters.increment("debt_incurred", loan.principal)
        
        # Immediately disburse any disbursements that are due at creation
        for disbursement in loan.disbursements_due(today):
            self.receive_debt(disbursement)
    
    def receive_debt(self, loan_disbursement: LoanDisbursement) -> None:
        credit = loan_disbursement.complete(self.calendar.today())
        self.take_credit(credit)
        self.counters.increment("debt_received", credit)
    
    def repay_debt(self, loan_payment: LoanPayment) -> None:
        loan_payment.complete(self.calendar.today())
        self.counters.increment("debt_repaid", loan_payment.amount_paid)
    
    def loan_disbursements_due(self) -> list[LoanDisbursement]:
        today = self.calendar.today()
        return [
            disbursement
            for loan in self._loans if loan.disbursement_due(today)
            for disbursement in loan.disbursement_schedule if disbursement.is_due(today)
        ]
    
    def loan_payments_due(self) -> list[tuple[Loan, LoanPayment]]:
        today = self.calendar.today()
        return [
            (loan, payment)
            for loan in self._loans if loan.payment_due(today)
            for payment in loan.payment_schedule if payment.is_due(today)
        ]


class Lender(Borrower):
    def __init__(self, *args, loan_options: list[dict] | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        # initialize agent counters
        self.counters.add_counters(
            "loans_created",
            type_ = int
        )
        
        self.counters.add_counters(
            "debt_created",
            "debt_disbursed",
            "debt_extinguished",
            "credit_issued",
            "credit_redeemed",
            type_ = Credit
        )
        
        self._loan_options: list[LoanOption] = [
            LoanOption(lender=self, **loan_option) for loan_option in (loan_options or [])
        ]
        
        self._received_loan_applications: deque[LoanApplication] = deque()
        
        self._loan_book: dict[Borrower, list[Loan]] = defaultdict(list)
        
        self.outstanding_credit: Credit = 0
    
    
    ###########
    # Methods #
    ###########
    
    def issue_credit(self, amount: Credit | float) -> Credit:
        """Creates credit and returns it. Increments `credit_issued` and updates `outstanding_credit`."""
        if amount <= 0:
            raise ValueError("'amount' must be positive.")
        credit = Credit(amount)
        self.outstanding_credit += credit
        self.counters.increment("credit_issued", credit)
        return credit
    
    def redeem_credit(self, credit: Credit) -> None:
        """Destroys credit. Increments `credit_redeemed` and updates `outstanding_credit`."""
        if not isinstance(credit, Credit):
            raise ValueError(f"'credit' must be a Credit instance, got {type(credit).__name__}")
        self.outstanding_credit -= credit
        self.counters.increment("credit_redeemed", credit)
    
    def create_debt(self, application: LoanApplication) -> Loan | None:
        if application.accepted and not application.closed:
            today = self.calendar.today()
            application.close(today)
            
            borrower = application.borrower
            loan = Loan(
                bank=self,
                borrower=borrower,
                date_issued=today,
                principal=application.principal,
                interest_rate=application.interest_rate,
                term=application.term,
                billing_window=application.billing_window,
            )
            self._loan_book[borrower].append(loan)
            self.counters.increment("loans_created")
            self.counters.increment("debt_created", loan.principal)
            return loan
    
    def disburse_debt(self, amount: Credit | float) -> Credit:
        credit = self.issue_credit(amount)
        self.counters.increment("debt_disbursed", credit)
        return credit
    
    def extinguish_debt(self, amount: Credit) -> None:
        self.redeem_credit(amount)
        self.counters.increment("debt_extinguished", amount)
    
    def loan_options(self, borrower: Borrower) -> list[LoanOption]:
        # returns a list of loans for which the borrower is eligible
        # for now it simply returns the whole list
        return self._loan_options
