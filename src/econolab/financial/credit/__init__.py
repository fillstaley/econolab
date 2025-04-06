"""Functionality for credit creation and destruction.

...

"""

from __future__ import annotations
from collections import defaultdict, deque

from ...core import BaseAgent
from .base import Credit


class InsufficientCreditError(Exception):
    pass

class Borrower(BaseAgent):
    def __init__(self, *args, debt_limit: int | float | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        # initialize agent counters
        self.counters.add_counters(
            "debt_incurred",
            "debt_repaid",
            "credit_taken",
            "credit_given",
            type_ = Credit,
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
    
    def loan_payments_due(self, date: int) -> list[tuple[Loan, LoanPayment]]:
        return [
            (loan, payment)
            for loan in self._loans if loan.payment_due(date)
            for payment in loan.payment_schedule if payment.is_due(date)
        ]


class Lender(Borrower):
    def __init__(self, *args, loan_options: list[dict] | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        # initialize agent counters
        self.counters.add_counters(
            "debt_created",
            "debt_extinguished",
            "credit_issued",
            "credit_redeemed",
        )
        
        self._loan_options: list[LoanOption] = [
            LoanOption(lender=self, **loan_option) for loan_option in (loan_options or [])
        ]
        
        self._received_loan_applications: deque[LoanApplication] = deque()
        
        self._loan_book: dict[Borrower, list[Loan]] = defaultdict(list)
        
        self.outstanding_credit: float = 0
    
    
    ###########
    # Methods #
    ###########
    
    def issue_credit(self, amount: float) -> Credit:
        """Creates credit and returns it. Increments `credit_issued` and updates `outstanding_credit`."""
        if amount <= 0:
            raise ValueError("'amount' must be positive.")
        credit = Credit(amount)
        self.outstanding_credit += float(credit)
        self.counters.increment("credit_issued", credit)
        return credit
    
    def redeem_credit(self, credit: Credit) -> None:
        """Destroys credit. Increments `credit_redeemed` and updates `outstanding_credit`."""
        if not isinstance(credit, Credit):
            raise ValueError(f"'credit' must be a Credit instance, got {type(credit).__name__}")
        self.outstanding_credit -= float(credit)
        self.counters.increment("credit_redeemed", credit)
    
    def loan_options(self, borrower: Borrower) -> list[LoanOption]:
        # returns a list of loans for which the borrower is eligible
        # for now it simply returns the whole list
        return self._loan_options

    def new_loan(self, application: LoanApplication, date: int) -> Loan | None:
        if application.approved and not application.issued:
            application.date_issued = date
            
            borrower = application.borrower
            
            loan = Loan(
                bank=self,
                borrower=borrower,
                date_issued=application.date_issued,
                principal=application.principal,
                interest_rate=application.interest_rate,
                term=application.term,
                billing_window=application.billing_window,
            )
            
            self._loan_book[borrower].append(loan)
            # TODO: disburse the principal
            
            return loan
    
    # FIXME: this method is broken
    def process_payment(self, borrower: Borrower, amount: float, date: int) -> bool:
        if success := self._account_book[borrower].debit(amount, repaid_debt=True):
            self._redeemed_credit += amount
        return success
    
    # TODO: implement this
    def close_loan(self,) -> bool:
        pass


class Loan:
    """Creates money."""

    def __init__(
        self,
        lender: Lender,
        borrower: Borrower,
        date_issued: int,
        principal: float,
        interest_rate: float = 0.0,
        term: int | None = None,
        billing_window: int = 0,
        payment_schedule: list[LoanPayment] | None = None,
    ) -> None:
        self.lender = lender
        self.borrower = borrower
        self.date_issued = date_issued
        self._principal = principal
        self.interest_rate = interest_rate
        self.term = term
        self.billing_window = billing_window
        
        self.payment_schedule = payment_schedule or [LoanPayment(principal, date_issued + term)]
    
    ##############
    # Properties #
    ##############
    
    @property
    def principal(self) -> float:
        return self._principal
    
    @property
    def due_date(self):
        return self.date_issued + self.term if self.term else None

    @property
    def interest(self):
        return self.principal * self.interest_rate * self.term if self.term else 0

    @property
    def amount_due(self):
        return self.principal + self.interest

    ###########
    # Methods #
    ###########
    
    def capitalize(self, amount: float):
        self._principal += amount
    
    def amortize(self, amount: float):
        self._principal -= amount
    
    def payment_due(self, date: int) -> bool:
        return any(payment.is_due(date) for payment in self.payment_schedule)
    
    def amount_due(self, date: int) -> float:
        return sum(payment.amount_due for payment in self.payment_schedule if payment.is_due(date))
    
    def pay(self, payment: LoanPayment, date: int):
        lender = self.lender
        borrower = self.borrower
        amount = payment.amount_due
        
        if success := lender.process_payment(borrower, amount, date):
            self.amortize(amount)
            payment.mark_paid(amount, date)
        return success


class LoanPayment:
    def __init__(
        self, 
        amount_due: float, 
        date_due: int, 
        billing_window: int = 0
    ) -> None:
        self.amount_due = amount_due
        self.date_due = date_due
        
        self.billing_window = billing_window
        
        self.amount_paid: float | None = None
        self.date_paid: int | None = None
    
    @property
    def paid(self) -> bool:
        return self.amount_paid is not None
    
    def is_due(self, date) -> bool:
        return not self.paid and date >= self.date_due - self.billing_window
    
    def mark_paid(self, amount_paid: float, date_paid: int) -> None:
        if not self.paid:
            self.amount_paid = amount_paid
            self.date_paid = date_paid


class LoanOption:
    def __init__(
        self,
        lender: Lender,
        term: int, 
        billing_window: int = 0,
        max_principal: float | None = None, 
        min_interest_rate: float = 0,
    ):
        self.lender = lender
        self.term = term
        self.billing_window = billing_window
        self.max_principal = max_principal
        self.min_interest_rate = min_interest_rate
    
    ###########
    # Methods #
    ###########
    
    def apply(self, borrower: Borrower, principal: float, date: int) -> LoanApplication:
        if self.max_principal:
            principal = max(principal, self.max_principal)
        
        return LoanApplication(
            lender=self.lender,
            borrower=borrower,
            date_opened=date,
            principal=principal,
            interest_rate=self.min_interest_rate,
            term=self.term,
            billing_window=self.billing_window,
        )


class LoanApplication:
    
    def __init__(self, 
        lender: Lender, 
        borrower: Borrower, 
        date_opened: int,
        principal: float, 
        interest_rate: float,
        term: int,
        billing_window: int,
    ):
        self.lender = lender
        self.borrower = borrower
        self.principal = principal
        self.interest_rate = interest_rate
        self.term = term
        self.billing_window = billing_window

        self.date_opened = date_opened
        self.date_reviewed = None
        self.date_closed = None
        self.date_issued = None
        
        self.approved = None
        self.accepted = None
        
        lender._received_loan_applications.append(self)
    
    ##############
    # Properties #
    ##############
    
    @property
    def closed(self) -> bool:
        return self.date_closed is not None
    
    @property
    def issued(self) -> bool:
        return self.date_issued is not None
    
    ###########
    # Methods #
    ###########
    
    def accept(self, date: int) -> Loan | None:
        # a loan should only be issued once
        if self.approved and not self.closed:
            self.date_closed = date

            return self.lender.new_loan(self, date)
