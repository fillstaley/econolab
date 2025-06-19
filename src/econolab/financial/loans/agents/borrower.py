"""...

...

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ....core import Debtor, InstrumentModelLike

if TYPE_CHECKING:
    from ....core import EconoCurrency, Instrument
    from ..base import Loan
    from ..model import LoanMarket
    from ..interfaces import LoanApplication, LoanRepayment


__all__ = [
    "Borrower",
]


class LoanModelLike(InstrumentModelLike):
    loan_market: LoanMarket


class Borrower(Debtor):
    """...
    
    ...
    """
    
    ##############
    # Attributes #
    ##############
    
    # instance attributes
    __slots__ = (
        "debt_limit",
        "loan_limit",
        "loan_application_limit",
        "_open_loans",
        "_closed_loans",
        "_open_loan_applications",
        "_closed_loan_application",
    )
    debt_limit: EconoCurrency | None
    loan_limit: int | None
    loan_application_limit: int | None
    _open_loans: list[Loan]
    _closed_loans: list[Loan]
    _open_loan_applications: list[LoanApplication]
    _closed_loan_application: list[LoanApplication]
    
    # class attributes
    default_debt_limit: int | float | None = None
    default_loan_limit: int | None = None
    default_loan_application_limit: int | None = None
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self,
        *args,
        debt_limit: int | float | None = None,
        loan_limit: int | None = None,
        loan_application_limit: int | None = None,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        
        if not isinstance(self.model, LoanModelLike):
            raise TypeError("'model' does not inherit from 'loans.LoanModel'")
        
        if debt_limit is None:
            debt_limit = self.default_debt_limit
        if not isinstance(debt_limit, int | float):
            raise TypeError(
                f"'debt_limit' must be an int or float; got {type(debt_limit).__name__}"
            )
        elif debt_limit < 0:
            raise ValueError(
                f"'debt_limit' must be nonnegative; got {debt_limit}"
            )
        
        if loan_limit is None:
            loan_limit = self.default_loan_limit
        if not isinstance(loan_limit, int):
            raise TypeError(
                f"'loan_limit' must be an int; got {type(loan_limit).__name__}"
            )
        elif loan_limit < 0:
            raise ValueError(
                f"'loan_limit' must be nonnegative; got {loan_limit}"
            )
        
        if loan_application_limit is None:
            loan_application_limit = self.default_loan_application_limit
        if not isinstance(loan_application_limit, int):
            raise TypeError(
                f"'loan_application_limit' must be an int; got {type(loan_application_limit).__name__}"
            )
        elif loan_application_limit < 0:
            raise ValueError(
                f"'loan_application_limit' must be nonnegative; got {loan_application_limit}"
            )

        # initialize agent counters
        self.counters.add_counters(
            "loans_incurred",
            type_ = int
        )

        self.counters.add_counters(
            "debt_incurred",
            "debt_repaid",
            type_ = self.Currency
        )
        
        self.debt_limit = self.Currency(debt_limit) if debt_limit is not None else debt_limit
        self.loan_limit = loan_limit
        self.loan_application_limit = loan_application_limit

        self._open_loans = []
        self._closed_loans = []
        self._open_loan_applications = []
        self._closed_loan_applications = []
    
    
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
    def debt_load(self) -> EconoCurrency:
        """Total principal value of all active loans.
        
        Returns
        -------
        float
            The sum of principal across all current loans held by the borrower.
        """
        return sum(
            (loan.principal for loan in self._open_loans),
            start=self.Currency(0)
        )
    
    @property
    def debt_capacity(self) -> EconoCurrency | bool:
        """Remaining debt the borrower can take on, given their limit.
        
        Returns
        -------
        float or bool
            The remaining capacity (in currency units) before reaching the debt limit,
            or True if no limit is set.
        """
        return max(self.Currency(0), self.debt_limit - self.debt_load) if self.debt_limit is not None else True
    
    
    ###########
    # Methods #
    ###########
    
    def loan_repayments_due(self) -> list[LoanRepayment]:
        """Return loan repayments that are due from the borrower.

        Parameters
        ----------
        date : EconoDate, optional
            The date to check for due payments. Defaults to the current model date.

        Returns
        -------
        list of LoanRepayment
            Repayments that are scheduled and due on the given date.
        """
        return [
            repayment
            for loan in self._open_loans if loan.repayment_due()
            for repayment in loan.repayment_schedule if repayment.due
        ]
    
    
    ###########
    # Actions #
    ###########
    
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
        for loan in self.search_for_loans(self.loan_application_limit or 1):
            if self.should_apply_for(loan, money_demand):
                application = loan.apply(self, self.Currency(money_demand))
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
            if self.can_accept_loan(app) and self.should_accept_loan(app):
                if loan := app.accept():
                    self._open_loans.append(loan)
                    self.counters.increment("loans_incurred")
                successes += 1
            else:
                app.reject()
        return successes
    
    def repay_loans(self, *due_repayments: LoanRepayment) -> int:
        """Attempt to make repayments on due loan installments.
        
        Parameters
        ----------
        *due_repayments : LoanRepayment
            Specific repayments to process. If none are provided, all due repayments are considered.
        
        Returns
        -------
        int
            The number of repayments successfully completed.
        """
        repayments = list(due_repayments) or self.loan_repayments_due()
        if not all(repayment.due for repayment in repayments):
            raise ValueError("All submitted repayments must be due; some are not.")
        
        if not due_repayments:
            self.prioritize_loan_payments(repayments)
        successes = 0
        for repayment in repayments:
            if not self.can_repay_loan(repayment) and self.should_repay_loan(repayment):
                break
            repayment.complete()
            successes += 1
        return successes
    
    
    #########
    # Hooks #
    #########
    
    # TODO: implement this
    def search_for_loans(self, limit: int = 1) -> list[type[Loan]]:
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
        if not isinstance(self.model, LoanModelLike):
            raise TypeError("'model' does not inherit from 'loans.LoanModel'")
        return self.model.loan_market.sample(self, limit)
    
    def can_apply_for(self, loan: Loan, money_demand: float) -> bool:
        """Check if the borrower is eligible to apply for a loan.
        
        This method can be overridden to define eligibility conditions for applications.
        
        Returns
        -------
        bool
            True if the borrower can apply, False otherwise.
        """
        return True
    
    def should_apply_for(self, loan: type[Loan], money_demand: float) -> bool:
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
    
    def prioritize_loan_payments(self, due_payments: list[LoanRepayment]) -> None:
        """Sort or reorder loan payments in-place before making them.
        
        This method can be overridden to define a payment prioritization strategy.
        """
        pass
    
    def can_repay_loan(self, due_payment: LoanRepayment) -> bool:
        """Check if the borrower has sufficient funds to make a loan payment.
        
        This method can be overridden to enforce eligibility or liquidity checks.
        
        Returns
        -------
        bool
            True if the borrower can make the payment, False otherwise.
        """
        return True
    
    def should_repay_loan(self, due_payment: LoanRepayment) -> bool:
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
    
    def _process_loan_disbursement(
        self,
        loan: Loan,
        /,
        amount: EconoCurrency
    ) -> None:
        self.counters.increment("debt_incurred", amount)
    
    def _make_loan_repayment(
        self,
        loan: Loan,
        /,
        amount: EconoCurrency,
        form: type[Instrument],
    ) -> None:
        self.give_money(to=loan.lender, amount=amount, form=form)
        self.counters.increment("debt_repaid", amount)
