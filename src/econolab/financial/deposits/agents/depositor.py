"""...

...

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ....core import EconoCreditor, InstrumentModelLike

if TYPE_CHECKING:
    from ..base import DepositAccount
    from ..model import DepositMarket


__all__ = [
    "Depositor",
]


class DepositModelLike(InstrumentModelLike):
    deposit_market: DepositMarket


class Depositor(EconoCreditor):
    """...
    
    ...
    """
    
    __slots__ = (
        "_open_deposit_applications",
        "_closed_deposit_applications",
    )
    _open_deposit_applications: list
    _closed_deposit_applications: list
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self._open_deposit_applications = []
        self._closed_deposit_applications = []
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def deposit_applications(self):
        return self._open_deposit_applications
    
    @property
    def deposit_offers(self):
        return [app for app in self.deposit_applications if app.reviewed]
    
    
    ###########
    # Actions #
    ###########
    
    def open_deposit_account(self) -> DepositAccount | None:
        """The agent attempts to open a deposit account.
        
        ...
        """
        offers = self.deposit_offers
        
        # TODO: limit the total number of (open) deposit applications
        if not offers:
            new_apps = self._apply_for_deposit_accounts()
            offers = [app for app in new_apps if app.reviewed]
        
        if offers:
            self.prioritize_deposit_offers(offers)
            return self._respond_to_deposit_offers(*offers)
    
    def close_deposit_account(self, account: DepositAccount) -> None:
        pass
    
    def deposit(self, account: DepositAccount, *assets):
        pass
    
    def withdraw(self, account: DepositAccount, amount):
        pass
    
    
    #########
    # Hooks #
    #########
    
    def prioritize_deposit_offers(self, offers) -> None:
        pass
    
    
    ##############
    # Primitives #
    ##############
    
    def _apply_for_deposit_accounts(self) -> list:
        ...
    
    def _respond_to_deposit_offers(self, *args) -> DepositAccount | None:
        ...
