"""...

...

"""

from __future__ import annotations

from typing import Generic, TypeVar

from ..agent import EconoAgent
from ..product import ProductMarket
from .base import EconoInstrument
from .agents import EconoIssuer


__all__ = [
    "InstrumentMarket",
]


S = TypeVar("S", bound=EconoIssuer)
P = TypeVar("P", bound=EconoInstrument)
D = TypeVar("D", bound=EconoAgent)

class InstrumentMarket(ProductMarket[S, P, D], Generic[S, P, D]):
    pass
