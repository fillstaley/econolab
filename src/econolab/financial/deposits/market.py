"""...

...

"""
from collections.abc import Mapping
from typing import Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import DepositAccount
    from .agents.issuer import DepositIssuer


class DepositMarket(Mapping):
    """A registry of available deposit accounts.

    Exposes a read-only dict-like interface to model components (e.g. depositors),
    while allowing deposit issuers to register and deregister their products 
    through controlled methods.

    The internal structure maps issuers to a list of deposit account classes.
    """

    def __init__(self, model) -> None:
        self._model = model
        self._products: dict[DepositIssuer, list[type[DepositAccount]]] = {}

    #####################
    # Mapping Interface #
    #####################

    def __getitem__(self, issuer: DepositIssuer) -> tuple[type[DepositAccount], ...]:
        if issuer not in self._products:
            raise KeyError(f"No products found for issuer {issuer}")
        return tuple(self._products[issuer])

    def __iter__(self) -> Iterator[DepositIssuer]:
        return iter(self._products)

    def __len__(self) -> int:
        return len(self._products)

    ########################
    # Modification Methods #
    ########################

    def register(self, *Accounts: type[DepositAccount]) -> None:
        """Registers an account class as an available product."""
        for Account in Accounts:
            if (issuer := Account.issuer) not in self._products:
                self._products[issuer] = []
            if Account not in self._products[issuer]:
                self._products[issuer].append(Account)

    def deregister(self, Account: type[DepositAccount]) -> None:
        """Removes an account class from its issuer's product list."""
        if (issuer := Account.issuer) in self and Account in self[issuer]:
            self._products[issuer].remove(Account)
            if not self._products[issuer]:
                del self._products[issuer]

    def clear_issuer(self, issuer: DepositIssuer) -> None:
        """Removes all account offerings from a given issuer."""
        self._products.pop(issuer, None)

    #######################
    # Convenience Methods #
    #######################

    def all_products(self) -> list[type[DepositAccount]]:
        """Returns a list of all available account classes."""
        return [
            Account
            for Accounts in self._products.values()
            for Account in Accounts
        ]
    
    def total_products(self) -> int:
        return len(self.all_products())

    def sample(self, k: int = 1) -> list[type[DepositAccount]]:
        """Returns a random sample of deposit account classes across all issuers."""
        from random import sample
        return sample(self.all_products(), k=min(k, self.total_products()))

    def search(self, predicate) -> list[type[DepositAccount]]:
        """Returns deposit account classes matching a given predicate."""
        return [
            Account for Account in self.all_products() if predicate(Account)
        ]
