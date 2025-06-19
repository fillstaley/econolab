"""...

...

"""

from __future__ import annotations

from typing import cast, TypeVar, TYPE_CHECKING

from ..agent import EconoAgent, EconoModelLike
from ..product import EconoProducer
from .base import EconoInstrument, InstrumentType

if TYPE_CHECKING:
    from .specs import InstrumentSpecification


__all__ = [
    "InstrumentModelLike",
    "EconoIssuer",
    "EconoDebtor",
    "EconoCreditor",
]


T = TypeVar("T", bound=EconoInstrument)


class InstrumentModelLike(EconoModelLike):
    pass


class EconoIssuer(EconoProducer):
    def _create_instrument_subclass(
        self,
        Instrument: type[T],
        specification: InstrumentSpecification,
        **kwargs
    ) -> type[T]:
        Meta = cast(InstrumentType, type(Instrument))
        Subclass = Meta(
            specification.name,
            (Instrument,),
            {
                "issuer": self,
                "Currency": self.Currency,
                **specification.to_dict(),
                **kwargs
            }
        )
        return cast(type[T], Subclass)


class EconoDebtor(EconoAgent):
    pass


class EconoCreditor(EconoAgent):
    pass
