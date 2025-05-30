"""...

...

"""

from __future__ import annotations

from ..._instrument import Creditor
from ..base import DepositAccount


class Depositor(Creditor):
    """...
    
    ...
    """
    
    __slots__ = (
        "_open_deposit_applications",
    )
    _open_deposit_applications: list
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self._open_deposit_applications = []
    
    
    ###########
    # Actions #
    ###########
    
    def open_deposit_account(self):
        if offers := [
            app for app in self._open_deposit_applications if app.reviewed
        ]:
            self.prioritize_deposit_offers(offers)
            if accepted := self._respond_to_deposit_offers(*offers):
                return accepted
        # Otherwise, search for and apply to new options
        return self._apply_for_deposit_accounts()
    
    def close_deposit_account(self):
        pass
    
    
    #########
    # Hooks #
    #########
    
    def prioritize_deposit_offers(self, offers):
        pass
    
    
    ##############
    # Primitives #
    ##############
    
    def _apply_for_deposit_accounts(self):
        pass
    
    def _respond_to_deposit_offers(self, *args):
        pass
