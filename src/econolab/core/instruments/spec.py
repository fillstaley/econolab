"""...

...

"""

from __future__ import annotations

from dataclasses import dataclass

from ..products import ProductSpecification


__all__ = [
    "InstrumentSpecification",
]


@dataclass(frozen=True, slots=True)
class InstrumentSpecification(ProductSpecification):
    def __post_init__(self) -> None:
        super(InstrumentSpecification, self).__post_init__()
    
    def to_dict(self) -> dict:
        return super(InstrumentSpecification, self).to_dict()
