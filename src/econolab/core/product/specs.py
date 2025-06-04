"""...

...

"""

from __future__ import annotations

from dataclasses import dataclass


__all__ = ["ProductSpecification",]


@dataclass(frozen=True, slots=True)
class ProductSpecification:
    name: str
    
    def __post_init__(self) -> None:
        pass
    
    def to_dict(self) -> dict:
        return {"name": self.name}
