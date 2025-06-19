"""...

...

"""

from __future__ import annotations

from ...core import EconoMeta


__all__ = [
    "EconoProduct",
    "ProductType",
]


class ProductType(EconoMeta):
    pass


class EconoProduct(metaclass=ProductType):
    pass
