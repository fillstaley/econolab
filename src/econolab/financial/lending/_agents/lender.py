"""...

...

"""


from __future__ import annotations

import logging
logger = logging.getLogger(__name__)

from collections import defaultdict, deque
from typing import TYPE_CHECKING

from ....temporal import EconoDate
from ...credit import Credit
from .borrower import Borrower

if TYPE_CHECKING:
    from .._interfaces.loan import Loan, LoanDisbursement, LoanPayment, LoanOption, LoanApplication


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
    # Methods #
    ###########
    
    def loan_disbursements_due(self, date: EconoDate | None = None) -> list[LoanDisbursement]:
        date = date or self.calendar.today()
        return [
            disbursement
            for disbursements in self._undisbursed_loans.values()
            for disbursement in disbursements if disbursement.is_due(date)
        ]
    
    
    ###########
    # Actions #
    ###########
    
    
    # TODO: this should be moved to a different agent, maybe
    def issue_credit(self, amount: Credit | float) -> Credit:
        """Creates credit and returns it. Increments `credit_issued` and updates `outstanding_credit`."""
        if amount <= 0:
            raise ValueError("'amount' must be positive.")
        credit = Credit(amount)
        self.outstanding_credit += credit
        self.counters.increment("credit_issued", credit)
        return credit
    
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
    
    
    ##############
    # Primitives #
    ##############
    
    def _create_application(
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
    
    def _create_debt(self, application: LoanApplication) -> Loan | None:
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
    
    def _disburse_debt(self, amount: Credit | float) -> Credit:
        debt = self.issue_credit(amount)
        self.counters.increment("debt_disbursed", debt)
        return debt
    
    # TODO: this should be moved to a different agent, maybe
    def _redeem_credit(self, credit: Credit) -> None:
        """Destroys credit. Increments `credit_redeemed` and updates `outstanding_credit`."""
        if not isinstance(credit, Credit):
            raise ValueError(f"'credit' must be a Credit instance, got {type(credit).__name__}")
        self.outstanding_credit -= credit
        self.counters.increment("credit_redeemed", credit)
    
    def _extinguish_debt(self, amount: Credit) -> None:
        self._redeem_credit(amount)
        self.counters.increment("debt_extinguished", amount)
