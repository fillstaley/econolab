"""...

...

"""

from collections.abc import Mapping


class DepositMarket(Mapping):
    def __init__(self, listings: dict):
        self._listings = listings

    def __getitem__(self, issuer):
        return self._listings[issuer]

    def __iter__(self):
        return iter(self._listings)

    def __len__(self):
        return len(self._listings)

    # Optional convenience methods
    def all_products(self):
        return [(issuer, cls) for issuer, classes in self._listings.items() for cls in classes]

    def sample(self, k=1):
        from random import sample
        all_classes = [cls for classes in self._listings.values() for cls in classes]
        return sample(all_classes, k=min(k, len(all_classes)))

    def search(self, predicate):
        return [
            cls for classes in self._listings.values()
            for cls in classes if predicate(cls)
        ]
