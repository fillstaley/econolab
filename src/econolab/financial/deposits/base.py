"""...

...

"""

from typing import TYPE_CHECKING

from .._currency import EconoCurrency
from .._instrument import Instrument

if TYPE_CHECKING:
    from .agents.deposit_holder import DepositHolder
    from .agents.depositor import Depositor


class DepositAccount(Instrument):
    """...
    
    ...
    """
    
    __slots__ = ("_creditor", "_balance",)
    
    Currency: type[EconoCurrency]
    
    _issuer: DepositHolder
    
    
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
    def issuer(self) -> DepositHolder:
        return self._issuer
    
    @property
    def debtor(self) -> DepositHolder:
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
