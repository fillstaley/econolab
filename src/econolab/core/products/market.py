"""...

...

"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Callable, Generic, Iterator, TypeVar, TYPE_CHECKING

from ..agent import EconoAgent
from .base import EconoProduct
from .agents import EconoSupplier

if TYPE_CHECKING:
    from ..model import EconoModel



__all__ = [
    "ProductMarket",
]


S = TypeVar("S", bound=EconoSupplier)
P = TypeVar("P", bound=EconoProduct)
D = TypeVar("D", bound=EconoAgent)


class ProductMarket(Mapping[S, tuple[type[P], ...]], Generic[S, P, D]):
    
    _model: EconoModel
    _products: dict[S, set[type[P]]]
    
    def __init__(self, model: EconoModel) -> None:
        self._model = model
        self._products = defaultdict(set)
    
    
    #####################
    # Mapping Interface #
    #####################
    
    def __getitem__(self, supplier: S) -> tuple[type[P], ...]:
        if supplier not in self._products:
            raise KeyError
        return tuple(self._products[supplier])
    
    def __iter__(self) -> Iterator[S]:
        return iter(self._products)
    
    def __len__(self) -> int:
        return len(self._products)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def model(self) -> EconoModel:
        return self._model
    
    
    ###########
    # Methods #
    ###########
    
    def all_products(self) -> list[type[P]]:
        """Returns a list of all available product classes on the market."""
        return [
            Product for Products in self._products.values() for Product in Products
        ]
    
    def total_products(self) -> int:
        """Returns the total number of product classes on the market."""
        return len(self.all_products())
    
    def register(self, supplier: S, *product_types: type[P]) -> None:
        """Adds product classes offered by an supplier to the market."""
        self._products[supplier].update(product_types)
    
    def deregister(self, supplier: S, *product_types: type[P]) -> None:
        """Removes product classes from a suppliers's list.
        
        Removes the supplier from the market if they no longer offer any
        product classes.
        """
        if supplier in self:
            self._products[supplier].difference_update(product_types)
            if not self[supplier]:
                self._products.pop(supplier)
    
    def sample(self, demander: D, k: int = 1) -> list[type[P]]:
        """Returns a random sample of product classes across all suppliers."""
        from random import sample
        eligible_products = self.all_products()
        return sample(self.all_products(), k=min(k, self.total_products()))
    
    def search(self, demander: D, predicate: Callable[[type[P]], bool]) -> list[type[P]]:
        """Returns product classes matching a given predicate."""
        return [
            Product for Product in self.all_products() if predicate(Product)
        ]
