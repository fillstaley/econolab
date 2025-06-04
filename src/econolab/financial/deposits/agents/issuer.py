"""...

...

"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import cast, Protocol, runtime_checkable, TYPE_CHECKING

from ..._instrument import Issuer, Debtor, InstrumentType
from ..base import DepositAccount
from ..specs import DepositSpecification
from .depositor import Depositor

if TYPE_CHECKING:
    from ..market import DepositMarket


__all__ = ["DepositIssuer",]


@runtime_checkable
class DepositModel(Protocol):
    deposit_market: DepositMarket


class DepositIssuer(Issuer, Debtor, Depositor):
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
        
        if not isinstance(self.model, DepositModel):
            raise TypeError(
                f"The 'model' attribute of {type(self).__name__} must inherit from DepositModel"
            )
        
        self._deposit_book = defaultdict(list)
        self._available_deposit_accounts = []
        self._received_deposit_applications = deque()
        
        if deposit_specs:
            self.create_deposit_class(*deposit_specs)
        
        self.model.deposit_market.register(self)
    
    
    ###########
    # Actions #
    ###########
    
    def create_deposit_class(self, *specs: DepositSpecification) -> None:
        for spec in specs:
            if not isinstance(spec, DepositSpecification):
                raise TypeError(
                    f"Expected DepositSpecification, got {type(spec).__name__} in create_deposit_class()"
                )
            
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
            self._deposit_book[Account] = []
            self.register_deposit_class(Account)
    
    def modify_deposit_class(self, Account: type[DepositAccount], /) -> None:
        ...
    
    def delete_deposit_class(self, Account: type[DepositAccount], /) -> None:
        ...
    
    def register_deposit_class(self, Account: type[DepositAccount], /) -> None:
        self._available_deposit_accounts.append(Account)
    
    def deregister_deposit_class(self, Account: type[DepositAccount], /) -> None:
        self._available_deposit_accounts.remove(Account)
    
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
