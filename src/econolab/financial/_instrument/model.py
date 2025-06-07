"""...

...

"""

from __future__ import annotations

from typing import cast, Generic, TypeVar, TYPE_CHECKING

from ...core import EconoModel
from ...core.product.market import ProductMarket, D
from .base import Instrument
from .agents import Issuer

if TYPE_CHECKING:
    from .model import InstrumentModel


__all__ = [
    "InstrumentModel",
    "InstrumentMarket",
]


class InstrumentModel(EconoModel):
    pass


S = TypeVar("S", bound=Issuer)
P = TypeVar("P", bound=Instrument)

class InstrumentMarket(ProductMarket[S, P, D], Generic[S, P, D]):
    @property
    def model(self) -> InstrumentModel:
        return cast(InstrumentModel, self._model)