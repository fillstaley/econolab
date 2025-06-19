"""...

...

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TYPE_CHECKING

from ...core import EconoDuration, InstrumentSpecification

if TYPE_CHECKING:
    from .agents import Borrower


__all__ = [
    "LoanSpecification",
]


@dataclass(frozen=True, slots=True)
class LoanSpecification(InstrumentSpecification):
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
    term: EconoDuration
    limit_per_borrower: int | None = 1
    limit_kind: Literal["outstanding", "cumulative"] = "outstanding"
    repayment_structure: Literal["bullet", "custom"] = "bullet"
    repayment_window: EconoDuration | None = None
    borrower_types: tuple[type[Borrower]] | None = None
    
    # TODO: add some logic for the default windows
    def __post_init__(self) -> None:
        super(LoanSpecification, self).__post_init__()
        
        # borrower_types defaults to the most general possible borrower in none are given
        if self.borrower_types is None:
            from .agents.borrower import Borrower
            object.__setattr__(self, "borrower_types", (Borrower,))
    
    def to_dict(self) -> dict:
        return {
            **super(LoanSpecification, self).to_dict(),
        }
