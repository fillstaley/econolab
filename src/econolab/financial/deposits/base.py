"""...

...

"""

from .._currency import EconoCurrency
from .._instrument import Instrument
from .agents.deposit_holder import DepositHolder
from .agents.depositor import Depositor


class DepositAccount(Instrument):
    """...
    
    ...
    """
    __slots__ = ("_creditor", "_balance",)
    
    issuer: DepositHolder
    Currency: type[EconoCurrency]
    
    debtor: DepositHolder
    creditor: Depositor
    
    
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
    
    
    @property
    def balance(self) -> EconoCurrency:
        return self._balance
    
    @property
    def creditor(self) -> Depositor:
        return self._creditor
    
    @property
    def depositor(self) -> Depositor:
        return self.creditor
    
    
    def credit(self, amount) -> None:
        self._balance += amount
    
    def debit(self, amount) -> None:
        self._balance -= amount
