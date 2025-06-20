"""A base class for all EconoLab interfaces.

Interfaces allow two (or more) agents to interact. Their purpose is to
allow agents to affect one another; that is, they ultimately endow
agents with a particular agency.

"""

from abc import ABC

from ..meta import EconoMeta


__all__ = [
    "EconoInterface",
    "InterfaceType",
]


class InterfaceType(EconoMeta):
    pass


class EconoInterface(ABC, metaclass=InterfaceType):
    pass
