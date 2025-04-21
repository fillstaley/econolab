"""...

...

"""

from ...core import BaseModel
from ._interfaces.loan import LoanMarket


class Model(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.loan_market = LoanMarket(self)
    
    def reset_counters(self) -> None:
        """Resets all of a model's (transient) counters to 0."""
        for counter in self.counters.transient.values():
            counter.reset()
