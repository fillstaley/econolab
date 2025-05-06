"""...

...

"""


from typing import Protocol, runtime_checkable


@runtime_checkable
class EconoModel(Protocol):
    pass


class EconoCurrency:
    _model: EconoModel
