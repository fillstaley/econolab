"""...

...

"""


from __future__ import annotations

import logging
logger = logging.getLogger(__name__)

from collections import defaultdict, deque
from typing import TYPE_CHECKING

from ...core import BaseAgent
from ...temporal import EconoDate
from ..credit import Credit

if TYPE_CHECKING:
    from .loan import Loan, LoanDisbursement, LoanPayment, LoanOption, LoanApplication


class InsufficientCreditError(Exception):
    pass

class Borrower(BaseAgent):
    APPLICATION_LIMIT: int = 3
    
    def __init__(
        self,
        *args,
        application_limit: int | None = None,
        debt_limit: int | float | None = None,
        **kwargs
    ) -> None:
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
        
        if application_limit is not None and (not isinstance(application_limit, int) or application_limit <= 0):
            raise ValueError(f"'application_limit' must be a positive int or None, got {application_limit}.")
        if debt_limit is not None and (not isinstance(debt_limit, int | float) or debt_limit < 0):
            raise ValueError(f"'debt_limit' must be a nonnegative number or None, got {debt_limit}.")
        
        self.application_limit = application_limit or self.APPLICATION_LIMIT
        self.debt_limit = debt_limit if debt_limit is not None else float("inf")
        
        self._open_loan_applications: list[LoanApplication] = []
        self._closed_loan_applications: list[LoanApplication] = []
        
        self._loans: list[Loan] = []
        
        self.credit: Credit = Credit(0)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def loan_offers(self) -> list[LoanApplication]:
        return [loan for loan in self._open_loan_applications if loan.reviewed]
    
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
    # Actions #
    ###########
    
    def apply_for_loans(self, money_demand: float) -> int:
        successes = 0
        for loan_option in self.search_for_loans(self.application_limit):
            if self.should_apply_for(loan_option, money_demand):
                application = loan_option._apply(self, money_demand, self.calendar.today())
                self._open_loan_applications.append(application)
                successes += 1
        return successes
    
    def respond_to_loan_offers(self, *loan_offers: LoanApplication) -> int:
        offers = list(loan_offers) or self.loan_offers
        if not all(app.reviewed for app in offers):
            raise ValueError("All submitted applications must be reviewed; some are not.")

        if not loan_offers:
            self.prioritize_loan_offers(offers)

        successes = 0
        for app in offers:
            today = self.calendar.today()
            if self.can_accept_loan(app) and self.should_accept_loan(app):
                if loan := app._accept(today):
                    self._loans.append(loan)
                    self.counters.increment("loans_incurred")
                    self.counters.increment("debt_incurred", loan.principal)
                    
                    # TODO: refactor this into a helper method
                    for disbursement in loan.disbursement_schedule:
                        disbursement._request(disbursement.amount_due, today)
                successes += 1
            else:
                app._reject(today)
        return successes
    
    def receive_loan_disbursements(self, *due_disbursements: LoanDisbursement) -> int:
        disbursements = list(due_disbursements) or self.loan_disbursements_owed()
        today = self.calendar.today()
        
        if not all(disbursement.is_due(today) for disbursement in disbursements):
            raise ValueError("All submitted disbursements must be due; some are not.")
        
        if not due_disbursements:
            self.prioritize_loan_disbursements_owed(disbursements)
        
        successes = 0
        for disbursement in disbursements:
            if not self.can_receive_disbursement(disbursement) and self.should_receive_disbursement(disbursement):
                break
            disbursement._complete(today)
            successes += 1
        return successes
    
    def make_loan_payments(self, *due_payments: LoanPayment) -> int:
        payments = list(due_payments) or self.loan_payments_due()
        today = self.calendar.today()
        
        if not all(payment.is_due(today) for payment in payments):
            raise ValueError("All submitted payments must be due; some are not.")
        
        if not due_payments:
            self.prioritize_loan_payments(payments)
        
        successes = 0
        for payment in payments:
            if not self.can_pay_loan(payment) and self.should_pay_loan(payment):
                break
            payment._complete(today)
            successes += 1
        return successes
    
    
    #########
    # Hooks #
    #########
    
    # TODO: implement this
    def search_for_loans(self, limit: int) -> list[LoanOption]:
        return []
    
    def can_apply_for(self, loan_option: LoanOption, money_demand: float) -> bool:
        return True
    
    def should_apply_for(self, loan_option: LoanOption, money_demand: float) -> bool:
        return True
    
    def prioritize_loan_offers(self, loan_options: list[LoanApplication]) -> None:
        pass
    
    def can_accept_loan(self, approved_application: LoanApplication) -> bool:
        return approved_application.approved
    
    def should_accept_loan(self, approved_application: LoanApplication) -> bool:
        return True
    
    def prioritize_loan_disbursements_owed(self, due_disbursements: list[LoanDisbursement]) -> None:
        pass
    
    def can_receive_disbursement(self, due_disbursement: LoanDisbursement) -> bool:
        return True
    
    def should_receive_disbursement(self, due_disbursement: LoanDisbursement) -> bool:
        return True
    
    def prioritize_loan_payments(self, due_payments: list[LoanPayment]) -> None:
        pass
    
    def can_pay_loan(self, due_payment: LoanPayment) -> bool:
        return self.credit >= due_payment.amount_due
    
    def should_pay_loan(self, due_payment: LoanPayment) -> bool:
        return True
    
    
    ###########
    # Methods #
    ###########
    
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
    
    def take_credit(self, credit: Credit) -> None:
        """Receive a quantity of credit and add it to the wallet. Increments `credit_taken`."""
        if not isinstance(credit, Credit):
            raise ValueError(f"'credit' should be an instance of Credit; got {type(credit).__name__}.")
        self.credit += credit
        self.counters.increment("credit_taken", credit)
    
    def repay_debt(self, debt: Credit) -> Credit:
        debt = self.give_credit(debt)
        self.counters.increment("debt_repaid", debt)
        return debt
    
    def receive_debt(self, debt: Credit) -> None:
        self.take_credit(debt)
        self.counters.increment("debt_received", debt)
    
    def loan_disbursements_owed(self, date: EconoDate | None = None) -> list[LoanDisbursement]:
        date = date or self.calendar.today()
        return [
            disbursement
            for loan in self._loans if loan.disbursement_due(date)
            for disbursement in loan.disbursement_schedule if disbursement.is_due(date)
        ]
    
    def loan_payments_due(self, date: EconoDate | None = None) -> list[LoanPayment]:
        date = date or self.calendar.today()
        return [
            payment
            for loan in self._loans if loan.payment_due(date)
            for payment in loan.payment_schedule if payment.is_due(date)
        ]


class Lender(Borrower):
    def __init__(
        self, 
        *args,
        loan_options: list[dict] | None = None,
        limit_loan_applications_reviewed: int | None = None,
        **kwargs
    ) -> None:
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
        
        self.limit_loan_applications_reviewed = limit_loan_applications_reviewed
        self._received_loan_applications: deque[LoanApplication] = deque()
        
        self._loan_book: dict[Borrower, list[Loan]] = defaultdict(list)
        self._undisbursed_loans: dict[Loan, list[LoanDisbursement]] = defaultdict(list)
        
        self.outstanding_credit: Credit = Credit(0)
    
    
    ###########
    # Actions #
    ###########
    
    def review_loan_applications(self, *received_applications: LoanApplication) -> int:
        applications = list(received_applications)
        
        if any(app.lender is not self for app in applications):
            raise ValueError(f"All submitted applications must be for {self}; some are not.")

        if not received_applications:
            N = min(
                self.limit_loan_applications_reviewed,
                len(self._received_loan_applications)
            )
            applications = [
                self._received_loan_applications.popleft() for _ in range(N)
            ]

        today = self.calendar.today()
        successes = 0
        for app in applications:
            if self.can_approve_loan(app) and self.should_approve_loan(app):
                app._approve(today)
                successes += 1
            # TODO: introduce deferred applications when lending becomes dynamic
            else:
                app._deny(today)
        return successes
    
    def make_loan_disbursements(self, *due_disbursements: LoanDisbursement) -> int:
        disbursements = list(due_disbursements) or self.loan_disbursements_due()
        today = self.calendar.today()
        
        if not all(disbursement.is_due(today) for disbursement in disbursements):
            raise ValueError("All submitted disbursements must be due; some are not.")
        
        if not due_disbursements:
            self.prioritize_loan_disbursements_due(disbursements)
        
        successes = 0
        for disbursement in disbursements:
            tomorrow = today + self.calendar.new_duration(1)
            expires_today = not disbursement.is_due(tomorrow)
            
            if self.can_disburse_loan(disbursement) and self.should_disburse_loan(disbursement):
                disbursement._complete(today)
                successes += 1
            elif expires_today:
                continue
            else:
                disbursement._expire(today)
            
            loan = disbursement.loan
            self._undisbursed_loans[loan].remove(disbursement)
            if not self._undisbursed_loans[loan]:
                del self._undisbursed_loans[loan]
        return successes
    
    
    #########
    # Hooks #
    #########
    
    def prioritize_loan_applications(self, applications: list[LoanApplication]):
        pass
    
    def can_approve_loan(self, application: LoanApplication) -> bool:
        return True
    
    def should_approve_loan(self, application: LoanApplication) -> bool:
        return True
    
    def prioritize_loan_disbursements_due(self, disbursements: list[LoanDisbursement]):
        pass
    
    def can_disburse_loan(self, disbursement: LoanDisbursement) -> bool:
        return True
    
    def should_disburse_loan(self, disbursement: LoanDisbursement) -> bool:
        return disbursement.requested
    
    
    ###########
    # Methods #
    ###########
    
    def loan_disbursements_due(self, date: EconoDate | None = None) -> list[LoanDisbursement]:
        date = date or self.calendar.today()
        return [
            disbursement
            for disbursements in self._undisbursed_loans.values()
            for disbursement in disbursements if disbursement.is_due(date)
        ]
    
    
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
    
    def create_application(
        self, 
        loan_option: LoanOption,
        borrower: Borrower, 
        principal: Credit, 
        date: EconoDate
    ) -> LoanApplication:
        application = LoanApplication(
            lender=self,
            borrower=borrower,
            principal=principal,
            date_opened=date,
            term=loan_option.term,
            interest_rate=loan_option.min_interest_rate
        )
        self._received_loan_applications.append(application)
        return application
    
    def create_loan(self, application: LoanApplication) -> Loan | None:
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
            self._undisbursed_loans[loan].extend(loan.disbursement_schedule)
            self.counters.increment("loans_created")
            self.counters.increment("debt_created", loan.principal)
            return loan
    
    def disburse_debt(self, amount: Credit | float) -> Credit:
        debt = self.issue_credit(amount)
        self.counters.increment("debt_disbursed", debt)
        return debt
    
    def extinguish_debt(self, amount: Credit) -> None:
        self.redeem_credit(amount)
        self.counters.increment("debt_extinguished", amount)
    
    def loan_options(self, borrower: Borrower) -> list[LoanOption]:
        # returns a list of loans for which the borrower is eligible
        # for now it simply returns the whole list
        return self._loan_options
