"""...

...

"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import cast, TYPE_CHECKING

from ....core import Issuer, Creditor, InstrumentType
from ..base import Loan
from ..spec import LoanSpecification
from .borrower import Borrower, LoanModelLike

if TYPE_CHECKING:
    from ....core import EconoCurrency, Instrument
    from ..base import LoanApplication


__all__ = [
    "Lender",
]


class Lender(Issuer, Creditor, Borrower):
    def __init__(
        self, 
        *args,
        loan_specs: list[LoanSpecification] | None = None,
        limit_loan_applications_reviewed: int | None = None,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        
        if not isinstance(self.model, LoanModelLike):
            raise TypeError("'model' does not inherit from 'loans.LoanModel'")
        
        # initialize agent counters
        self.counters.add_counters(
            "loans_created",
            type_ = int
        )
        
        self.counters.add_counters(
            "loan_funds_disbursed",
            "loan_funds_redeemed",
            type_ = self.Currency
        )
        
        self._loan_book: dict[type[Loan], list[Loan]] = defaultdict(list)
        
        if loan_specs:
            self.create_loan_class(*loan_specs)
        
        self.limit_loan_applications_reviewed = limit_loan_applications_reviewed
        self._received_loan_applications: deque[LoanApplication] = deque()
        
        self.outstanding_credit: EconoCurrency = self.Currency(0)
    
    
    ###########
    # Methods #
    ###########
    
    
    ###########
    # Actions #
    ###########
    
    def create_loan_class(self, *specs: LoanSpecification) -> None:
        """Create a LoanOption for the lender from a predefined LoanSpecs template.

        This method constructs a loan offering by combining a lender's identity with
        the structural and financial parameters provided by a LoanSpecs instance.
        Optionally, borrower eligibility can be constrained by passing one or more
        borrower types. If no borrower types are provided, defaults to all borrowers.

        Parameters
        ----------
        specs : LoanSpecs
            The specification template defining the loan's term, limits, rates, and structure.
        date_created : EconoDate
            The date the loan option is created and potentially made available.
        *borrower_types : type[Borrower]
            Optional list of borrower types eligible to apply for this loan.
        """
        for spec in specs:
            if not isinstance(spec, LoanSpecification):
                raise TypeError(
                    f"Expected LoanSpecification, got {type(spec).__name__}"
                )
            
            Sub = InstrumentType(
                spec.name,
                (Loan,),
                {
                    "lender": self,
                    "Currency": self.Currency,
                    **spec.to_dict()
                }
            )
            Sub = cast(type[Loan], Sub)
            self._loan_book[Sub] = []
            self.register_loan_class(Sub)
    
    def modify_loan_class(self, LoanSub: type[Loan]) -> None:
        raise NotImplemented
    
    def remove_loan_option(self, LoanSub: type[Loan]) -> None:
        raise NotImplemented
    
    def register_loan_class(self, *LoanSubs: type[Loan]) -> None:
        if not isinstance(self.model, LoanModelLike):
            raise TypeError("'model' does not inherit from 'loans.LoanModel'")
        self.model.loan_market.register(self, *LoanSubs)
    
    def deregister_loan_class(self, *LoanSubs: type[Loan]) -> None:
        if not isinstance(self.model, LoanModelLike):
            raise TypeError("'model' does not inherit from 'loans.LoanModel'")
        self.model.loan_market.deregister(self, *LoanSubs)
    
    def review_loan_applications(self, *received_applications: LoanApplication) -> int:
        applications = list(received_applications)
        
        if any(app.lender is not self for app in applications):
            raise ValueError(f"All submitted applications must be for {self}; some are not.")

        if not received_applications:
            N = len(self._received_loan_applications)
            if self.limit_loan_applications_reviewed is not None:
                N = min(N, self.limit_loan_applications_reviewed)
            applications = [
                self._received_loan_applications.popleft() for _ in range(N)
            ]

        successes = 0
        for app in applications:
            if self.can_approve_loan(app) and self.should_approve_loan(app):
                app.approve(app.principal_requested, app.minimum_interest_rate)
                successes += 1
            # TODO: introduce deferred applications when lending becomes dynamic
            else:
                app.deny()
        return successes
    
    
    #########
    # Hooks #
    #########
    
    def prioritize_loan_applications(self, applications: list[LoanApplication]) -> None:
        pass
    
    def can_approve_loan(self, application: LoanApplication) -> bool:
        return True
    
    def should_approve_loan(self, application: LoanApplication) -> bool:
        return True
    
    
    ##############
    # Primitives #
    ##############
    
    def _register_loan_application(self, application: LoanApplication, /) -> None:
        self._received_loan_applications.append(application)
    
    def _register_loan_instance(self, loan: Loan, /) -> None:
        self._loan_book[type(loan)].append(loan)
        self.counters.increment("loans_created")
        
    def _make_loan_disbursement(
        self,
        loan: Loan,
        /,
        amount: EconoCurrency,
        form: type[Instrument],
    ) -> None:
        self.give_money(to=loan.borrower, amount=amount, form=form)
        self.counters.increment("loan_funds_disbursed", amount)
    
    def _process_loan_repayment(
        self,
        loan: Loan,
        /,
        amount: EconoCurrency
    ) -> None:
        self.counters.increment("loan_funds_redeemed", amount)
