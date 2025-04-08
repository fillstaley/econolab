"""Functionality for credit creation and destruction.

...

"""

import logging

logger = logging.getLogger(__name__)

from __future__ import annotations
from collections import defaultdict, deque

from ...core import BaseAgent
from ...temporal import EconoDate, EconoDuration
from ..credit import Credit


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


class Loan:
    """Creates money."""
    
    
    ###################
    # Special Methods #
    ###################

    def __init__(
        self,
        lender: Lender,
        borrower: Borrower,
        date_issued: EconoDate,
        principal: Credit,
        interest_rate: float = 0.0,
        term: EconoDuration | None = None,
        disbursement_schedule: list[LoanDisbursement] | None = None,
        payment_schedule: list[LoanPayment] | None = None,
    ) -> None:
        self.lender = lender
        self.borrower = borrower
        self.date_issued = date_issued
        self._principal = principal
        self.interest_rate = interest_rate
        self.term = term
        
        self.disbursement_schedule = disbursement_schedule or [LoanDisbursement(self, principal, date_issued)]
        self.payment_schedule = payment_schedule or [LoanPayment(self, principal, date_issued + term)]
    
    def __repr__(self) -> str:
        return f"<Loan of {self.principal} from {self.lender} to {self.borrower} on {self.date_issued}>"
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def principal(self) -> Credit:
        return self._principal
    
    @property
    def due_date(self) -> EconoDate:
        return self.date_issued + self.term if self.term else None

    @property
    def interest(self) -> Credit:
        return self.principal * self.interest_rate * self.term if self.term else 0

    @property
    def amount_due(self) -> Credit:
        return self.principal + self.interest

    ###########
    # Methods #
    ###########
    
    def capitalize(self, amount: Credit) -> None:
        self._principal += amount
    
    def amortize(self, amount: Credit) -> None:
        self._principal -= amount
    
    def disbursement_due(self, date: EconoDate) -> bool:
        return any(disbursement.is_due(date) for disbursement in self.disbursement_schedule)
    
    def disbursement_amount(self, date: EconoDate) -> Credit:
        return sum(disbursement.amount_due for disbursement in self.disbursement_schedule if disbursement.is_due(date))
    
    def disbursements_due(self, date: EconoDate) -> set[LoanDisbursement]:
        return {disbursement for disbursement in self.disbursement_schedule if disbursement.is_due(date)}
    
    def payment_due(self, date: EconoDate) -> bool:
        return any(payment.is_due(date) for payment in self.payment_schedule)
    
    def payment_amount(self, date: EconoDate) -> Credit:
        return sum(payment.amount_due for payment in self.payment_schedule if payment.is_due(date))
    
    def payments_due(self, date: EconoDate) -> set[LoanPayment]:
        return {payment for payment in self.payment_schedule if payment.is_due(date)}


class LoanDisbursement:
    __slots__ =(
        "_loan",
        "_amount_due",
        "_date_due",
        "_disbursement_window",
        "_amount_disbursed",
        "_date_disbursed"
    )
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self,
        loan: Loan,
        amount_due: Credit,
        date_due: EconoDate,
        disbursement_window: EconoDuration = EconoDuration(0)
    ) -> None:
        self._loan = loan
        self._amount_due = amount_due
        self._date_due = date_due
        self._disbursement_window = disbursement_window
        
        self._amount_disbursed: Credit | None = None
        self._date_disbursed: EconoDate | None = None
    
    def __repr__(self) -> str:
        status = "disbursed" if self.disbursed else "undisbursed"
        return f"<LoanDisbursement of {self.amount_due} for {self.loan} due on {self.date_due} ({status})>"
    
    def __str__(self) -> str:
        status = "Disbursed" if self.disbursed else "Undisbursed"
        return f"Loan disbursement of {self.amount_due} due on {self.date_due} ({status})"
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def loan(self) -> Loan:
        return self._loan
    
    @property
    def amount_due(self) -> Credit:
        return self._amount_due
    
    @property
    def date_due(self) -> EconoDate:
        return self._date_due
    
    @property
    def disbursement_window(self) -> EconoDuration:
        return self._disbursement_window
    
    @property
    def disbursed(self) -> bool:
        return bool(self._amount_disbursed)
    
    @property
    def amount_disbursed(self) -> Credit | None:
        return self._amount_disbursed
    
    @property
    def date_disbursed(self) -> EconoDate | None:
        return self._date_disbursed
    
    
    ###########
    # Methods #
    ###########
    
    def is_due(self, date: EconoDate) -> bool:
        return (
            not self.disbursed and
            self.date_due <= date <= self.date_due + self.disbursement_window
        )
    
    def complete(self, date: EconoDate) -> Credit:
        if self.disbursed:
            logger.debug(f"LoanDisbursement already disbursed on {self._date_disbursed}: disburse() call ignored.")
            return None
        elif not self.is_due(date):
            logger.warning(f"Attempted disbursement of {self} outside of window.")
            return None
        credit = self.loan.lender.disburse_debt(self.amount_due)
        self._amount_disbursed = credit
        self._date_disbursed = date
        return credit


class LoanPayment:
    __slots__ = (
        "_loan",
        "_amount_due",
        "_date_due",
        "_payment_window",
        "_amount_paid",
        "_date_paid",
    )
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self,
        loan: Loan,
        amount_due: Credit, 
        date_due: EconoDate, 
        payment_window: EconoDuration = EconoDuration(0)
    ) -> None:
        self._loan = loan
        self._amount_due = amount_due
        self._date_due = date_due
        self._payment_window = payment_window
        
        self._amount_paid: Credit | None = None
        self._date_paid: EconoDuration | None = None
    
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
    def amount_due(self) -> Credit:
        return self._amount_due
    
    @property
    def date_due(self) -> EconoDate:
        return self._date_due
    
    @property
    def payment_window(self) -> EconoDuration:
        return self._payment_window
    
    @property
    def paid(self) -> bool:
        return bool(self._amount_paid)
    
    @property
    def amount_paid(self) -> Credit | None:
        return self._amount_paid
    
    @property
    def date_paid(self) -> EconoDate | None:
        return self._date_paid
    
    
    ###########
    # Methods #
    ###########
    
    def is_due(self, date: EconoDate) -> bool:
        return not self.paid and date >= self.date_due - self.payment_window
    
    def is_overdue(self, date: EconoDate) -> bool:
        return not self.paid and date > self.date_due
    
    def complete(self, date: EconoDate):
        if self.paid:
            logger.debug(f"LoanPayment already paid on {self._date_paid}: pay() call ignored.")
            return False
        credit = self.loan.borrower.give_credit(self.amount_due)
        self.loan.lender.extinguish_debt(credit)
        self._amount_paid = credit
        self._date_paid = date
        return True


class LoanOption:
    def __init__(
        self,
        lender: Lender,
        term: EconoDuration, 
        max_principal: Credit | None = None, 
        min_interest_rate: float = 0,
    ):
        self.lender = lender
        self.term = term
        self.max_principal = max_principal
        self.min_interest_rate = min_interest_rate
    
    ###########
    # Methods #
    ###########
    
    def apply(self, borrower: Borrower, principal: Credit, date: EconoDate) -> LoanApplication:
        if self.max_principal:
            principal = max(principal, self.max_principal)
        
        return LoanApplication(
            lender=self.lender,
            borrower=borrower,
            date_opened=date,
            principal=principal,
            interest_rate=self.min_interest_rate,
            term=self.term,
        )


class LoanApplication:
    
    def __init__(self, 
        lender: Lender, 
        borrower: Borrower, 
        date_opened: EconoDate,
        principal: Credit, 
        interest_rate: float,
        term: EconoDuration,
    ):
        self.lender = lender
        self.borrower = borrower
        self.principal = principal
        self.interest_rate = interest_rate
        self.term = term

        self._date_opened = date_opened
        
        self._approved: bool = False
        self._date_reviewed: EconoDate | None = None
        
        self._accepted: bool = False
        self._date_decided: EconoDate | None = None
        
        self._date_closed: EconoDate | None = None
        
        
        lender._received_loan_applications.append(self)
        logger.debug(
            f"LoanApplication created on {date_opened} by {borrower} and submitted to {lender}."
        )
    
    ##############
    # Properties #
    ##############
    
    @property
    def reviewed(self) -> bool:
        return bool(self._date_reviewed)
    
    @property
    def approved(self) -> bool:
        return self._approved
    
    @property
    def denied(self) -> bool:
        return self.reviewed and not self.approved
    
    @property
    def decided(self) -> bool:
        return bool(self._date_decided)
    
    @property
    def accepted(self) -> bool:
        return self._accepted
    
    @property
    def rejected(self) -> bool:
        return self.decided and not self.accepted
    
    @property
    def closed(self) -> bool:
        return bool(self._date_closed)
    
    
    ###########
    # Methods #
    ###########
    
    def approve(self, date: EconoDate) -> None:
        if self.reviewed:
            logger.debug("LoanApplication is already reviewed: approval attempt ignored.")
            return
        self._approved = True
        self._date_reviewed = date
        logger.info(f"LoanApplication approved by {self.lender} on {date}.")
    
    def deny(self, date: EconoDate) -> None:
        if self.reviewed:
            logger.debug("LoanApplication is already reviewed: denial attempt ignored.")
            return
        self._date_reviewed = date
        logger.info(f"LoanApplication rejected by {self.lender} on {date}.")
    
    def accept(self, date: EconoDate) -> Loan | None:
        if self.decided:
            logger.warning("LoanApplication is already decided: acceptance attempt ignored.")
            return
        if not self.approved:
            logger.warning("LoanApplication is not approved: cannot accept.")
            return
        self._accepted = True
        self._date_decided = date
        logger.info(f"LoanApplication accepted by {self.borrower} on {date}.")
        return self.lender.create_debt(self, date)
    
    def reject(self, date: EconoDate) -> None:
        if self.decided:
            logger.warning("LoanApplication is already decided: rejection attempt ignored.")
            return
        self._date_decided = date
        logger.info(f"LoanApplication rejected by {self.borrower} on {date}.")
    
    def close(self, date: EconoDate) -> None:
        self._date_closed = date
