"""...

...

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...core import EconoInstrument

if TYPE_CHECKING:
    from ...core import EconoDuration, EconoCurrency
    from .agents import Depositor, DepositIssuer


__all__ = [
    "DepositAccount",
]


class DepositAccount(EconoInstrument):
    """...
    
    ...
    """
    
    __slots__ = (
        "_depositor",
        "_balance",
    )
    _depositor: Depositor
    _balance: EconoCurrency
    
    depository_institution: DepositIssuer
    maturity_period: EconoDuration | None
    withdrawal_limit_count: int | None
    withdrawal_limit_value: EconoCurrency | None
    withdrawal_limit_period: EconoDuration | None
    minimum_balance: EconoCurrency | None
    overdraft_limit: EconoCurrency | None
    
    
    def __init__(self, depositor: Depositor, init_balance: EconoCurrency | None = None) -> None:
        self._depositor = depositor
        if init_balance is None:
            self._balance = self.Currency()
        elif isinstance(init_balance, self.Currency):
            self._balance = init_balance
        else:
            raise TypeError(
                f"'init_balance' needs to be of type {self.Currency.__name__}; "
                f"got {type(init_balance).__name__} instead."
            )
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def balance(self) -> EconoCurrency:
        return self._balance
    
    @property
    def debtor(self) -> DepositIssuer:
        return self.depository_institution
    
    @property
    def creditor(self) -> Depositor:
        return self.depositor
    
    @property
    def depositor(self) -> Depositor:
        return self._depositor
    
    
    ###########
    # Methods #
    ###########
    
    def credit(self, amount) -> None:
        self._balance += amount
    
    def debit(self, amount) -> None:
        self._balance -= amount
