"""...

...

"""


from __future__ import annotations

import logging
logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

from ....core import BaseAgent
from ....temporal import EconoDate
from ...credit import Credit
from .._interfaces.loan import Loan, LoanDisbursement, LoanPayment, LoanOption, LoanApplication



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
        """List of reviewed but undecided loan applications.
        
        Returns
        -------
        list of LoanApplication
            The open applications that have been reviewed by lenders.
        """
        return [loan for loan in self._open_loan_applications if loan.reviewed]
    
    @property
    def debt_load(self) -> float:
        """Total principal value of all active loans.
        
        Returns
        -------
        float
            The sum of principal across all current loans held by the borrower.
        """
        return sum(loan.principal for loan in self._loans) if self._loans else 0
    
    @property
    def debt_capacity(self) -> float | bool:
        """Remaining debt the borrower can take on, given their limit.
        
        Returns
        -------
        float or bool
            The remaining capacity (in currency units) before reaching the debt limit,
            or True if no limit is set.
        """
        return max(0, self.debt_limit - self.debt_load) if self.debt_limit is not None else True
    
    
    ###########
    # Methods #
    ###########
    
    def loan_disbursements_owed(self, date: EconoDate | None = None) -> list[LoanDisbursement]:
        """Return loan disbursements that are owed to the borrower.

        Parameters
        ----------
        date : EconoDate, optional
            The date to check for due disbursements. Defaults to the current model date.

        Returns
        -------
        list of LoanDisbursement
            Disbursements that are scheduled and due on the given date.
        """
        date = date or self.calendar.today()
        return [
            disbursement
            for loan in self._loans if loan.disbursement_due(date)
            for disbursement in loan.disbursement_schedule if disbursement.is_due(date)
        ]
    
    def loan_payments_due(self, date: EconoDate | None = None) -> list[LoanPayment]:
        """Return loan payments that are due from the borrower.

        Parameters
        ----------
        date : EconoDate, optional
            The date to check for due payments. Defaults to the current model date.

        Returns
        -------
        list of LoanPayment
            Payments that are scheduled and due on the given date.
        """
        date = date or self.calendar.today()
        return [
            payment
            for loan in self._loans if loan.payment_due(date)
            for payment in loan.payment_schedule if payment.is_due(date)
        ]
    
    
    ###########
    # Actions #
    ###########
    
    # TODO: this should be moved to a different agent, maybe
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
    
    def apply_for_loans(self, money_demand: float) -> int:
        """
        Apply for loan options based on the borrower's demand for credit.
        
        Parameters
        ----------
        money_demand : float
            The amount of credit the borrower is seeking.
        
        Returns
        -------
        int
            The number of applications successfully submitted.
        """
        successes = 0
        for loan_option in self.search_for_loans(self.application_limit):
            if self.should_apply_for(loan_option, money_demand):
                application = loan_option._apply(self, money_demand, self.calendar.today())
                self._open_loan_applications.append(application)
                successes += 1
        return successes
    
    def respond_to_loan_offers(self, *loan_offers: LoanApplication) -> int:
        """
        Respond to reviewed loan offers by accepting or rejecting them.
        
        Parameters
        ----------
        *loan_offers : LoanApplication
            Specific loan offers to respond to. If none are provided, all reviewed offers are considered.
        
        Returns
        -------
        int
            The number of loan offers successfully accepted.
        """
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
    
    # TODO: change this to a method for requesting disbursements
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
        """
        Attempt to make payments on due loan installments.
        
        Parameters
        ----------
        *due_payments : LoanPayment
            Specific payments to process. If none are provided, all due payments are considered.
        
        Returns
        -------
        int
            The number of payments successfully completed.
        """
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
        """Return a list of available loan options up to a specified limit.
        
        This method can be overridden to define how a borrower searches for loan opportunities.
        
        Parameters
        ----------
        limit : int
            The maximum number of loan options to return.
        
        Returns
        -------
        list of LoanOption
            The loan options visible to this borrower.
        """
        
        if getattr(self.model, "loan_market", None) is not None:
            return self.model.loan_market.sample(self)
    
    def can_apply_for(self, loan_option: LoanOption, money_demand: float) -> bool:
        """Check if the borrower is eligible to apply for a loan.
        
        This method can be overridden to define eligibility conditions for applications.
        
        Returns
        -------
        bool
            True if the borrower can apply, False otherwise.
        """
        return True
    
    def should_apply_for(self, loan_option: LoanOption, money_demand: float) -> bool:
        """Determine whether the borrower wants to apply for a given loan.
        
        This method can be overridden to implement behavioral logic or preferences.
        
        Returns
        -------
        bool
            True if the borrower chooses to apply, False otherwise.
        """
        return True
    
    def prioritize_loan_offers(self, loan_options: list[LoanApplication]) -> None:
        """Sort or reorder loan offers in-place before responding to them.
        
        This method can be overridden to define a prioritization strategy.
        """
        pass
    
    def can_accept_loan(self, approved_application: LoanApplication) -> bool:
        """Check if the borrower is able to accept a loan application.
        
        This method can be overridden to apply eligibility checks before accepting.
        
        Returns
        -------
        bool
            True if the borrower can accept, False otherwise.
        """
        return approved_application.approved
    
    def should_accept_loan(self, approved_application: LoanApplication) -> bool:
        """Determine whether the borrower wants to accept a loan offer.
        
        This method can be overridden to encode preferences or strategic behavior.
        
        Returns
        -------
        bool
            True if the borrower wants to accept the offer, False otherwise.
        """
        return True
    
    def prioritize_loan_disbursements_owed(self, due_disbursements: list[LoanDisbursement]) -> None:
        """Sort or reorder loan disbursements in-place before requesting them.
        
        This method can be overridden to define disbursement prioritization logic.
        """
        pass
    
    def can_receive_disbursement(self, due_disbursement: LoanDisbursement) -> bool:
        """Check if the borrower can receive a due disbursement.
        
        This method can be overridden to enforce eligibility or timing conditions.
        
        Returns
        -------
        bool
            True if the borrower can receive the disbursement, False otherwise.
        """
        return True
    
    def should_receive_disbursement(self, due_disbursement: LoanDisbursement) -> bool:
        """Determine whether the borrower wants to receive a disbursement.
        
        This method can be overridden to define behavioral preferences.
        
        Returns
        -------
        bool
            True if the borrower wants the disbursement, False otherwise.
        """
        return True
    
    def prioritize_loan_payments(self, due_payments: list[LoanPayment]) -> None:
        """Sort or reorder loan payments in-place before making them.
        
        This method can be overridden to define a payment prioritization strategy.
        """
        pass
    
    def can_pay_loan(self, due_payment: LoanPayment) -> bool:
        """Check if the borrower has sufficient funds to make a loan payment.
        
        This method can be overridden to enforce eligibility or liquidity checks.
        
        Returns
        -------
        bool
            True if the borrower can make the payment, False otherwise.
        """
        return self.credit >= due_payment.amount_due
    
    def should_pay_loan(self, due_payment: LoanPayment) -> bool:
        """Determine whether the borrower wants to make a payment.
        
        This method can be overridden to encode repayment preferences or behaviors.
        
        Returns
        -------
        bool
            True if the borrower chooses to pay, False otherwise.
        """
        return True
    
    
    ##############
    # Primitives #
    ##############
    
    # TODO: maybe this should be a (passive) action
    def _take_credit(self, credit: Credit) -> None:
        """Receive credit and increase the borrower's wallet balance.
        
        Parameters
        ----------
        credit : Credit
            The credit amount to add.
        
        Raises
        ------
        ValueError
            If the credit is not an instance of Credit.
        
        Notes
        -----
        This method increments the 'credit_taken' counter.
        """
        if not isinstance(credit, Credit):
            raise ValueError(f"'credit' should be an instance of Credit; got {type(credit).__name__}.")
        self.credit += credit
        self.counters.increment("credit_taken", credit)
    
    def _receive_debt(self, debt: Credit) -> None:
        """Record newly received debt and update wallet and counters.
        
        Parameters
        ----------
        debt : Credit
            The amount of debt received by the borrower.
        
        Notes
        -----
        This method wraps `_take_credit()` and increments the 'debt_received' counter.
        """
        self._take_credit(debt)
        self.counters.increment("debt_received", debt)
    
    def _repay_debt(self, debt: Credit) -> Credit:
        """Repay debt by transferring credit and updating counters.
        
        Parameters
        ----------
        debt : Credit
            The amount of debt to repay.
        
        Returns
        -------
        Credit
            The credit amount that was repaid.
        
        Notes
        -----
        This method uses `give_credit()` and increments the 'debt_repaid' counter.
        """
        debt = self.give_credit(debt)
        self.counters.increment("debt_repaid", debt)
        return debt
