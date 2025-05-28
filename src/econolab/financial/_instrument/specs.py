"""...

...

"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InstrumentSpecification:
    name: str