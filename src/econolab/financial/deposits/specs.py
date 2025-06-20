"""...

...

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...core import InstrumentSpecification

if TYPE_CHECKING:
    from ...core import EconoDuration, EconoCurrency


__all__ = [
    "DepositSpecification",
]


@dataclass(frozen=True, slots=True)
class DepositSpecification(InstrumentSpecification):
    """...
    
    ...
    """
    maturity_period: EconoDuration | None = None
    withdrawal_limit_count: int | None = None
    withdrawal_limit_value: EconoCurrency | None = None
    withdrawal_limit_period: EconoDuration | None = None
    minimum_balance: EconoCurrency | None = None
    overdraft_limit: EconoCurrency | None = None
    
    def __post_init__(self) -> None:
        super(DepositSpecification, self).__post_init__()
    
    def to_dict(self) -> dict:
        return super(DepositSpecification, self).to_dict()
