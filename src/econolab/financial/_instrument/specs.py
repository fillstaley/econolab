"""...

...

"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InstrumentSpecification:
    name: str
    
    def __post_init__(self) -> None:
        pass
    
    def to_dict(self) -> dict:
        return {}