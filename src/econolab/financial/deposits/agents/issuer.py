"""...

...

"""

from typing import cast, TYPE_CHECKING

from ..._instrument import Issuer, Debtor, InstrumentType
from ..base import DepositAccount
from ..specs import DepositSpecification
from .depositor import Depositor

if TYPE_CHECKING:
    from ..model import DepositModel


class DepositIssuer(Issuer, Debtor, Depositor):
    """...
    
    ...
    """
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self._deposit_account_classes: list[type[DepositAccount]]
    
    
    ###########
    # Actions #
    ###########
    
    def create_deposit_class(self, *specs: DepositSpecification) -> None:
        for spec in specs:
            Account = InstrumentType(
                spec.name,
                (DepositAccount,),
                {
                    "_issuer": self,
                    "Currency": self.Currency,
                    **spec.to_dict()
                }
            )
            Account = cast(type[DepositAccount], Account)
            self._deposit_account_classes.append(Account)
            
            if not isinstance(self.model, DepositModel):
                raise RuntimeError
            self.model.deposit_market
    
    def modify_deposit_class(self, Account: DepositAccount, /) -> None:
        ...
    
    def delete_deposit_class(self, Account: DepositAccount, /) -> None:
        ...
    
    def register_deposit_class(self, Account: DepositAccount, /) -> None:
        ...
    
    def deregister_deposit_class(self, Account: DepositAccount, /) -> None:
        ...
    
    def review_deposit_applications(self, *applications) -> int:
        successes = 0
        for app in applications:
            if self.can_approve_deposit(app) and self.should_approve_deposit(app):
                successes += 1
                app._approve(self.calendar.today())
            # TODO: introduce deferred applications later
            else:
                app._deny(self.calendar.today())
        return successes
    
    
    #########
    # Hooks #
    #########
    
    def prioritize_deposit_applications(self):
        ...
    
    def can_approve_deposit(self, application):
        ...
    
    def should_approve_deposit(self, application):
        ...
