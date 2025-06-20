"""...

...

"""

from __future__ import annotations

from typing import cast, TypeVar, TYPE_CHECKING

from ..products import EconoProducer
from .base import EconoInstrument, InstrumentType

if TYPE_CHECKING:
    from .spec import InstrumentSpecification


__all__ = [
    "EconoIssuer",
]


T = TypeVar("T", bound=EconoInstrument)


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
