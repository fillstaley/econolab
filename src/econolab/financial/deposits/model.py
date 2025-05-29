"""...

...

"""

from ...core import EconoModel
from .market import DepositMarket


class DepositModel(EconoModel):
    """...
    
    ...
    """
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.deposit_market = DepositMarket(self)
