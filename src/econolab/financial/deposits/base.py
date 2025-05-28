"""...

...

"""

from typing import TYPE_CHECKING

from ...temporal import EconoDuration, EconoDate
from .._currency import EconoCurrency
from .._instrument import Instrument

if TYPE_CHECKING:
    from .agents.issuer import Issuer
    from .agents.depositor import Depositor


class DepositAccount(Instrument):
    """...
    
    ...
    """
    
    __class_constants__ = ("_issuer", "Currency")
    __slots__ = ("_creditor", "_balance",)
    
    _issuer: Issuer
    Currency: type[EconoCurrency]
    
    maturity_period: EconoDuration | None
    withdrawal_limit_count: int | None
    withdrawal_limit_value: EconoCurrency | None
    withdrawal_limit_period: EconoDuration | None
    minimum_balance: EconoCurrency | None
    overdraft_limit: EconoCurrency | None
    
    
    def __init__(self, depositor: Depositor, init_balance: EconoCurrency | None = None) -> None:
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
    def issuer(self) -> Issuer:
        return self._issuer
    
    @property
    def debtor(self) -> Issuer:
        return self.issuer
    
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
