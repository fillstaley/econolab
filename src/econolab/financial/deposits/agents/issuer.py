"""...

...

"""

from typing import cast

from ... import _instrument as instrument
from ..base import DepositAccount
from ..specs import DepositSpecification


class Issuer(instrument.Issuer, instrument.Debtor):
    """...
    
    ...
    """
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self._deposit_account_types: list[type[DepositAccount]]
    
    
    ###########
    # Methods #
    ###########
    
    def create_deposit_account_class(self, spec: DepositSpecification) -> None:
        Account = instrument.InstrumentType(
            spec.name,
            (DepositAccount,),
            {
                "_issuer": self,
                "Currency": self.Currency,
                **spec.to_dict()
            }
        )
        Account = cast(type[DepositAccount], Account)
        self._deposit_account_types.append(Account)
