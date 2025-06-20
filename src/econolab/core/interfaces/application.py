"""...

...

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import EconoInterface

if TYPE_CHECKING:
    from ...core import EconoAgent, EconoDate


__all__ = [
    "EconoApplication",
]


class EconoApplication(EconoInterface):
    __slots__ = (
        "_applicant",
        "_date_opened",
        "_date_reviewed",
        "_date_closed",
        "_approved",
        "_accepted",
    )
    _applicant: EconoAgent
    _date_opened: EconoDate
    _date_reviewed: EconoDate | None
    _date_closed: EconoDate | None
    _approved: bool
    _accepted: bool
    
    
    def __init__(
        self,
        applicant: EconoAgent,
    ) -> None:
        self._applicant = applicant
        
        self._date_opened = applicant.calendar.today()
        self._date_reviewed = None
        self._date_closed = None
        self._approved = False
        self._accepted = False
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def applicant(self) -> EconoAgent:
        return self._applicant
    
    @property
    def date_opened(self) -> EconoDate:
        return self._date_opened
    
    @property
    def date_reviewed(self) -> EconoDate | None:
        return self._date_reviewed
    
    @property
    def date_closed(self) -> EconoDate | None:
        return self._date_closed
    
    
    ##########
    # States #
    ##########
    
    @property
    def open(self) -> bool:
        return not self.closed
    
    @property
    def reviewed(self) -> bool:
        return self.date_reviewed is not None
    
    @property
    def closed(self) -> bool:
        return self.date_closed is not None
    
    @property
    def approved(self) -> bool:
        return self.reviewed and self._approved
    
    @property
    def denied(self) -> bool:
        return self.reviewed and not self.approved
    
    @property
    def accepted(self) -> bool:
        return self.closed and self._accepted
    
    @property
    def rejected(self) -> bool:
        return self.closed and not self.accepted
    
    
    ###########
    # Methods #
    ###########
    
    def _review(self) -> bool:
        if not self.reviewed:
            self._date_reviewed = self.applicant.calendar.today()
            return True
        return False
    
    def _close(self) -> bool:
        if not self.closed:
            self._date_closed = self.applicant.calendar.today()
            return True
        return False
