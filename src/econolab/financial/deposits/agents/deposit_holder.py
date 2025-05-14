"""...

...

"""

from ..._instrument import Issuer, Debtor
from ..base import DepositAccount


class DepositHolder(Issuer, Debtor):
    """...
    
    ...
    """
    
    def offer_instrument(self, base: DepositAccount) -> None:
        pass