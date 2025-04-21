"""...

...

"""


from __future__ import annotations

import logging
logger = logging.getLogger(__name__)

from dataclasses import dataclass, asdict
from typing import Literal, Protocol, runtime_checkable, TYPE_CHECKING

from ....temporal import EconoDate, EconoDuration
from ...credit import Credit

if TYPE_CHECKING:
    from .._agents.borrower import Borrower
    from .._agents.lender import Lender



class RandomLike(Protocol):
    pass

@runtime_checkable
class ABFModel(Protocol):
    random: RandomLike


class LoanMarket:
    """A centralized interface for loan coordination between borrowers and lenders."""
    
    ###################
    # Special Methods #
    ###################
    
    def __call__(self, borrower: Borrower, date: EconoDate) -> LoanOption | None:
        """Return a random eligible and available loan option for this borrower."""
        options = self.search(borrower, date)
        return self.model.random.choice(options) if options else None

    def __init__(self, model: ABFModel, /):
        self.model = model
        self._options: list[LoanOption] = []
    
    
    ###########
    # Methods #
    ###########
    
    def register(self, option: LoanOption):
        """Add a loan option to the market."""
        self._options.append(option)

    def deregister(self, option: LoanOption):
        """Remove a loan option from the market."""
        self._options.remove(option)
    
    def sample(self, borrower: Borrower, k: int = 1) -> list[LoanOption]:
        """Return a random sample of loan options for a borrower.
        
        ...
        """
        options = self.search(borrower)
        return self.model.random.sample(options, k) if options else []

    def search(
        self,
        borrower: Borrower,
        date: EconoDate | None = None,
        lender: Lender | None = None
    ) -> list[LoanOption]:
        """Return the whole list of loan options for a borrower."""
        if date is None:
            date = self.model.calendar.today()
        
        filtered_options = [
            option for option in self._options
            if option.is_available(date or self.calendar.today())
            and option.is_eligible(borrower)
        ]
        
        if lender:
            filtered_options = [
                option for option in filtered_options if option.lender is lender
            ]
        
        return filtered_options


@dataclass(frozen=True)
class LoanSpecs:
    """
    Immutable specifications for a class of loans.

    A LoanSpecs object defines the structural and financial characteristics of a loan
    that may be offered by one or more lenders. These specs serve as blueprints
    for constructing LoanOption instances during model initialization or runtime.

    Attributes
    ----------
    name : str
        Human-readable name for the loan specification (also used for factory naming).
    term : EconoDuration
        Duration of the loan in model time units.
    limit_per_borrower : int or None
        Maximum number of concurrent loans of this type allowed per borrower.
    limit_kind : {"outstanding", "cumulative"}
        Constraint type applied to the loan limit.
    disbursement_structure : {"bullet", "custom"}
        Disbursement scheduling pattern
    payment_structure : {"bullet", "custom"}
        Repayment scheduling pattern
    """
    name: str
    term: EconoDuration
    limit_per_borrower: int | None = 1
    limit_kind: Literal["outstanding", "cumulative"] = "outstanding"
    disbursement_structure: Literal["bullet", "custom"] = "bullet"
    disbursement_window: EconoDuration = EconoDuration(0)
    payment_structure: Literal["bullet", "custom"] = "bullet"
    payment_window: EconoDuration = EconoDuration(0)
    borrower_types: tuple[type[Borrower]] | None = None
    
    def __post_init__(self) -> None:
        # borrower_types defaults to the most general possible borrower in none are given
        if self.borrower_types is None:
            from .._agents.borrower import Borrower
            object.__setattr__(self, "borrower_types", (Borrower,))
    
    def to_dict(self) -> dict:
        return asdict(self)


class LoanOption:
    
    @classmethod
    def from_specifications(
        cls,
        loan_specs: LoanSpecs,
        /,
        lender: Lender,
        date_created: EconoDate,
        *,
        min_principal: Credit | None = None,
        max_principal: Credit | None = None,
        min_interest_rate: float | None = None,
        max_interest_rate: float | None = None,
        available_from: EconoDate | None = None,
        available_until: EconoDate | None = None
    ) -> LoanOption:
        return cls(
            lender,
            date_created,
            **loan_specs.to_dict(),
            min_principal=min_principal,
            max_principal=max_principal,
            min_interest_rate=min_interest_rate,
            max_interest_rate=max_interest_rate,
            available_from=available_from,
            available_until=available_until
        )
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self,
        lender: Lender,
        date_created: EconoDate,
        name: str,
        term: EconoDuration,
        limit_per_borrower: int | None,
        limit_kind: Literal["outstanding", "cumulative"],
        disbursement_structure: Literal["bullet", "custom"],
        disbursement_window: EconoDuration,
        payment_structure: Literal["bullet", "custom"],
        payment_window: EconoDuration,
        borrower_types: tuple[type[Borrower]],
        *,
        min_principal: Credit | None = None,
        max_principal: Credit | None = None,
        min_interest_rate: float | None = None,
        max_interest_rate: float | None = None,
        available_from: EconoDate | None = None,
        available_until: EconoDate | None = None
    ):
        self._lender = lender
        self._date_created = date_created
        
        self._name = name
        self._term = term
        self._limit_per_borrower = limit_per_borrower
        self._limit_kind = limit_kind
        self._disbursement_structure = disbursement_structure
        self._disbursement_window = disbursement_window
        self._payment_structure = payment_structure
        self._payment_window = payment_window
        self._borrower_types = borrower_types
        
        self._min_principal = min_principal or Credit(0)
        self._max_principal = max_principal
        self._min_interest_rate = min_interest_rate
        self._max_interest_rate = max_interest_rate or min_interest_rate
        self._available_from = available_from or date_created
        self._available_until = available_until or EconoDate.max()
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def lender(self) -> Lender:
        return self._lender
    
    @property
    def date_created(self) -> EconoDate:
        return self._date_created
    
    @property
    def term(self) -> EconoDuration:
        return self._term
    
    @property
    def borrower_types(self) -> tuple[type[Borrower], ...]:
        return self._borrower_types
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def limit_per_borrower(self) -> int | None:
        return self._limit_per_borrower
    
    @property
    def limit_kind(self) -> Literal["outstanding", "cumulative"]:
        return self._limit_kind
    
    @property
    def min_principal(self) -> Credit | None:
        return self._min_principal
    
    @property
    def max_principal(self) -> Credit | None:
        return self._max_principal
    
    @property
    def min_interest_rate(self) -> float | None:
        return self._min_interest_rate
    
    @property
    def max_interest_rate(self) -> float | None:
        return self._max_interest_rate
    
    @property
    def available_from(self) -> EconoDate:
        return self._available_from
    
    @property
    def available_until(self) -> EconoDate:
        return self._available_until
    
    ###############
    # Update Method
    ###############
    
    def update(
        self,
        *,
        min_principal: Credit | None = None,
        max_principal: Credit | None = None,
        min_interest_rate: float | None = None,
        max_interest_rate: float | None = None,
        available_from: EconoDate | None = None,
        available_until: EconoDate | None = None,
    ) -> None:
        if min_principal is not None:
            self._min_principal = min_principal
        if max_principal is not None:
            self._max_principal = max_principal
        if min_interest_rate is not None:
            self._min_interest_rate = min_interest_rate
        if max_interest_rate is not None:
            self._max_interest_rate = max_interest_rate
        if available_from is not None:
            self._available_from = available_from
        if available_until is not None:
            self._available_until = available_until
    
    ###############
    # Other Methods
    ###############
    
    def is_available(self, date: EconoDate) -> bool:
        return self._available_from <= date <= self._available_until
    
    def is_eligible(self, borrower: Borrower) -> bool:
        return (
            isinstance(borrower, self.borrower_types)
            and len(self.lender._loan_book[borrower]) < self.limit_per_borrower
        )
    
    def _apply(self, borrower: Borrower, principal: Credit | int | float, date: EconoDate) -> LoanApplication:
        if self.max_principal:
            principal = min(principal, self.max_principal)
            principal = Credit(principal)
        
        return self.lender._create_application(self, borrower, principal, date)


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
    
    def _approve(self, date: EconoDate) -> None:
        if self.reviewed:
            logger.debug("LoanApplication is already reviewed: approval attempt ignored.")
            return
        self._approved = True
        self._date_reviewed = date
        logger.info(f"LoanApplication approved by {self.lender} on {date}.")
    
    def _deny(self, date: EconoDate) -> None:
        if self.reviewed:
            logger.debug("LoanApplication is already reviewed: denial attempt ignored.")
            return
        self._date_reviewed = date
        logger.info(f"LoanApplication rejected by {self.lender} on {date}.")
    
    def _accept(self, date: EconoDate) -> Loan | None:
        if self.decided:
            logger.warning("LoanApplication is already decided: acceptance attempt ignored.")
            return
        if not self.approved:
            logger.warning("LoanApplication is not approved: cannot accept.")
            return
        self._accepted = True
        self._date_decided = date
        logger.info(f"LoanApplication accepted by {self.borrower} on {date}.")
        return self.lender._create_debt(self, date)
    
    def _reject(self, date: EconoDate) -> None:
        if self.decided:
            logger.warning("LoanApplication is already decided: rejection attempt ignored.")
            return
        self._date_decided = date
        logger.info(f"LoanApplication rejected by {self.borrower} on {date}.")
    
    def _close(self, date: EconoDate) -> None:
        self._date_closed = date


class Loan:
    """Creates money."""
    
    # TODO: implement this
    @classmethod
    def from_application(cls, loan_application: LoanApplication) -> Loan:
        raise NotImplemented

    
    ###################
    # Special Methods #
    ###################

    def __init__(
        self,
        lender: Lender,
        borrower: Borrower,
        date_created: EconoDate,
        principal: Credit,
        interest_rate: float = 0.0,
        term: EconoDuration | None = None,
        disbursement_structure: LoanDisbursementStructure | None = None,
        disbursement_window: EconoDuration = EconoDuration(0),
        payment_structure: LoanPaymentStructure | None = None,
        payment_window: EconoDuration = EconoDuration(0)
    ) -> None:
        self.lender = lender
        self.borrower = borrower
        self.date_issued = date_created
        self._principal = principal
        self.interest_rate = interest_rate
        self.term = term
        self.disbursement_window = disbursement_window
        self.payment_structure = payment_structure
        self.payment_window = payment_window
        
        self.disbursement_schedule = (
            disbursement_structure(self) if disbursement_structure else
            get_disbursement_structure("bullet")(self)
        )
        self.payment_schedule = []
    
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
    
    def disbursements_due(self, date: EconoDate) -> list[LoanDisbursement]:
        return {disbursement for disbursement in self.disbursement_schedule if disbursement.is_due(date)}
    
    def payment_due(self, date: EconoDate) -> bool:
        return any(payment.is_due(date) for payment in self.payment_schedule)
    
    def payment_amount(self, date: EconoDate) -> Credit:
        return sum(payment.amount_due for payment in self.payment_schedule if payment.is_due(date))
    
    def payments_due(self, date: EconoDate) -> list[LoanPayment]:
        return {payment for payment in self.payment_schedule if payment.is_due(date)}


class LoanDisbursementStructure:
    def __init__(
        self,
        name: str,
        rule: callable[Loan, list[LoanDisbursement]]
    ) -> None:
        self._name = name
        self._rule = rule
    
    def __repr__(self) -> str:
        return f"<LoanDisbursementStructure '{self.name}'>"
    
    def __str__(self) -> str:
        return f"{self.name.capitalize()} loan disbursement structure"
    
    def __call__(self, loan: Loan) -> list[LoanDisbursement]:
        return self._rule(loan)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def name(self) -> str:
        return self._name


class LoanDisbursement:
    __slots__ =(
        "_loan",
        "_amount_due",
        "_date_due",
        "_disbursement_window",
        "_amount_requested",
        "_date_requested",
        "_status",
        "_amount_disbursed",
        "_date_disbursed",
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
        
        # for now, set the amount requested to be the amount due
        # ie. we assume all loans disbursements are requested by default
        self._amount_requested: Credit | None = None
        self._date_requested: EconoDate | None = None
        
        self._status: Literal["pending", "requested", "completed", "expired"] = "requested"
        self._amount_disbursed: Credit | None = None
        self._date_disbursed: EconoDate | None = None
    
    def __repr__(self) -> str:
        return f"<LoanDisbursement of {self.amount_due} for {self.loan} due on {self.date_due} ({self.status})>"
    
    def __str__(self) -> str:
        return f"Loan disbursement of {self.amount_due} due on {self.date_due} ({self.status})"
    
    
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
    def amount_requested(self) -> Credit | None:
        return self._amount_requested
    
    @property
    def date_requested(self) -> EconoDate | None:
        return self._date_requested
    
    @property
    def amount_disbursed(self) -> Credit | None:
        return self._amount_disbursed
    
    @property
    def date_disbursed(self) -> EconoDate | None:
        return self._date_disbursed
    
    @property
    def status(self) -> str:
        return self._status
    
    @property
    def pending(self) -> bool:
        return self._status == "pending"
    
    @property
    def requested(self) -> bool:
        return self._status == "requested"
    
    @property
    def completed(self) -> bool:
        return self._status == "completed"
    
    @property
    def expired(self) -> bool:
        return self._status == "expired"
    
    @property
    def disbursed(self) -> bool:
        return self._status in {"completed", "expired"}
    
    
    ###########
    # Methods #
    ###########
    
    def is_due(self, date: EconoDate) -> bool:
        return (
            not self.disbursed and
            self.date_due <= date <= self.date_due + self.disbursement_window
        )
    
    def past_due(self, date: EconoDate) -> bool:
        return date >= self.date_due + self.disbursement_window
    
    def _request(self, amount: Credit | int | float, date: EconoDate) -> bool:
        if self.requested:
            logger.debug(f"LoanDisbursement was requested on {self._date_requested}: _request() call ignored.")
            return False
        elif self.disbursed:
            logger.debug(f"LoanDisbursement was disbursed on {self._date_disbursed}: _request() call ignored.")
            return False
        elif self.past_due(date):
            logger.debug(f"LoanDisbursement was due on {self._date_due}: _request() call ignored.")
            return False
        self._amount_requested = amount
        self._date_requested = date
        return True
    
    def _complete(self, date: EconoDate) -> bool:
        if self.disbursed:
            logger.debug(f"LoanDisbursement was disbursed on {self._date_disbursed}: _complete() call ignored.")
            return False
        elif not self.is_due(date):
            logger.warning(f"Attempted disbursement of {self} outside of payment window.")
            return False
        debt = self.loan.lender._disburse_debt(self.amount_due)
        self.loan.borrower._receive_debt(debt)
        self._amount_disbursed = debt
        self._date_disbursed = date
        
        self.loan.payment_schedule.extend(self.loan.payment_structure(self))
        
        self._status = "completed"
        logger.info(f"Disbursement for {self.loan} completed on {date}.")
        return True
    
    def _expire(self, date: EconoDate) -> bool:
        if self.disbursed:
            logger.debug(f"LoanDisbursement was disbursed on {self._date_disbursed}: _expire() call ignored.")
            return False
        elif not self.past_due(date):
            logger.debug("LoanDisbursement could still be completed: _expire() call ignored.")
            return False
        self._amount_disbursed = None
        self._date_disbursed = date
        self._status = "expired"
        logger.info(f"Disbursement for {self.loan} expired on {date}.")
        return True


class LoanPaymentStructure:
    def __init__(
        self,
        name: str,
        rule: callable[LoanDisbursement, list[LoanPayment]]
    ) -> None:
        self._name = name
        self._rule = rule
    
    def __repr__(self) -> str:
        return f"<LoanPaymentStructure '{self.name}'>"
    
    def __str__(self) -> str:
        return f"{self.name.capitalize()} loan payment structure"
    
    def __call__(self, loan_disbursement: LoanDisbursement) -> list[LoanPayment]:
        return self._rule(loan_disbursement)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def name(self) -> str:
        return self._name


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
    
    def _complete(self, date: EconoDate):
        if self.paid:
            logger.debug(f"LoanPayment already paid on {self._date_paid}: pay() call ignored.")
            return False
        elif not self.is_due(date):
            logger.warning(f"Attempted payment of {self} outside of billing window.")
            return False
        debt = self.loan.borrower._repay_debt(self.amount_due)
        self.loan.lender._extinguish_debt(debt)
        self._amount_paid = debt
        self._date_paid = date
        return True


def bullet_loan_disbursement_structure(loan: Loan) -> list[LoanDisbursement]:
    return [LoanDisbursement(loan, loan.principal, loan.date_created, loan.disbursement_window)]

BULLET_DISBURSEMENT = LoanDisbursementStructure("bullet", rule = bullet_loan_disbursement_structure)

DISBURSEMENT_STRUCTURES = {
    "bullet": BULLET_DISBURSEMENT
}

def get_disbursement_structure(name: str) -> LoanDisbursementStructure:
    return DISBURSEMENT_STRUCTURES[name]


def bullet_loan_payment_structure(loan_disbursement: LoanDisbursement) -> list[LoanPayment]:
    return [
        LoanPayment(
            loan_disbursement,
            loan_disbursement.principal,
            loan_disbursement.date_disbursed + loan_disbursement.loan.term,
            loan_disbursement.loan.payment_window
        )
    ]

BULLET_PAYMENT = LoanPaymentStructure("bullet", rule = bullet_loan_payment_structure)

PAYMENT_STRUCTURES = {
        "bullet": BULLET_PAYMENT
}

def get_payment_structure(name: str) -> LoanPaymentStructure:
    return PAYMENT_STRUCTURES[name]
