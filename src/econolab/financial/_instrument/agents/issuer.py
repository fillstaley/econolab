"""...

...

"""

from abc import ABC, abstractmethod

from ....core import EconoAgent
from ..base import Instrument

class Issuer(EconoAgent, ABC):
    """...
    
    ...
    """
    
    @abstractmethod
    def offer_instrument(self, base: Instrument) -> None:
        pass
