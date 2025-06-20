"""...

...

"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import TYPE_CHECKING

from ....core import EconoIssuer, EconoModelLike
from ..base import DepositAccount
from ..specs import DepositSpecification

if TYPE_CHECKING:
    from ....core import EconoCurrency, EconoInstrument
    from ..model import DepositMarket


__all__ = [
    "DepositIssuer",
]


class DepositModelLike(EconoModelLike):
    deposit_market: DepositMarket


class DepositIssuer(EconoIssuer):
    """...
    
    ...
    """
    
    __slots__ = (
        "_deposit_book",
        "_available_deposit_accounts",
        "_received_deposit_applications",
    )
    _deposit_book: dict[type[DepositAccount], list[DepositAccount]]
    _available_deposit_accounts: list[type[DepositAccount]]
    _received_deposit_applications: deque
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self,
        *args,
        deposit_specs: list[DepositSpecification] | None = None,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        
        if not isinstance(self.model, DepositModelLike):
            raise TypeError("'model' does not inherit from 'deposits.DepositModel'")
        
        self._deposit_book = defaultdict(list)
        self._available_deposit_accounts = []
        self._received_deposit_applications = deque()
        
        if deposit_specs:
            self.create_deposit_class(*deposit_specs)
    
    
    ###########
    # Actions #
    ###########
    
    def create_deposit_class(self, *specs: DepositSpecification) -> None:
        for spec in specs:
            if not isinstance(spec, DepositSpecification):
                raise TypeError(
                    f"Expected DepositSpecification, got {type(spec).__name__}"
                )
            
            Subclass = self._create_instrument_subclass(DepositAccount, spec, depository_institution=self)
            self._deposit_book[Subclass] = []
            self.register_deposit_class(Subclass)
    
    def modify_deposit_class(self, DepositSub: type[DepositAccount], /) -> None:
        raise NotImplemented
    
    def delete_deposit_class(self, DepositSub: type[DepositAccount], /) -> None:
        raise NotImplemented
    
    def register_deposit_class(self, *DepositSubs: type[DepositAccount]) -> None:
        if not isinstance(self.model, DepositModelLike):
            raise TypeError("'model' does not inherit from 'deposits.DepositModel'")
        self.model.deposit_market.register(self, *DepositSubs)
    
    def deregister_deposit_class(self, *DepositSubs: type[DepositAccount]) -> None:
        if not isinstance(self.model, DepositModelLike):
            raise TypeError("'model' does not inherit from 'deposits.DepositModel'")
        self.model.deposit_market.deregister(self, *DepositSubs)
    
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
