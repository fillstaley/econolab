"""...

...

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...core import Instrument

if TYPE_CHECKING:
    from ...core import EconoDuration, EconoCurrency
    from .agents import Depositor, DepositIssuer


__all__ = [
    "DepositAccount",
]


class DepositAccount(Instrument):
    """...
    
    ...
    """
    
    __slots__ = ("_debtor", "_creditor", "_balance",)
    
    __class_constants__ = ("issuer", "Currency")
    issuer: DepositIssuer
    Currency: type[EconoCurrency]
    
    maturity_period: EconoDuration | None
    withdrawal_limit_count: int | None
    withdrawal_limit_value: EconoCurrency | None
    withdrawal_limit_period: EconoDuration | None
    minimum_balance: EconoCurrency | None
    overdraft_limit: EconoCurrency | None
    
    
    def __init__(self, depositor: Depositor, init_balance: EconoCurrency | None = None) -> None:
        self._debtor = self.issuer
        self._creditor = depositor
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
    def debtor(self) -> DepositIssuer:
        return self._debtor
    
    @property
    def creditor(self) -> Depositor:
        return self._creditor
    
    @property
    def depositor(self) -> Depositor:
        return self.creditor
    
    @property
    def balance(self) -> EconoCurrency:
        return self._balance
    
    
    ###########
    # Methods #
    ###########
    
    def credit(self, amount) -> None:
        self._balance += amount
    
    def debit(self, amount) -> None:
        self._balance -= amount
