"""...

...

"""

from __future__ import annotations

from .._instrument.model import InstrumentModel
from .market import DepositMarket


class DepositModel(InstrumentModel):
    """...
    
    ...
    """
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.deposit_market = DepositMarket(self)
