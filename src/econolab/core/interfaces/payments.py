"""...

...

"""

from __future__ import annotations

from typing import cast, TYPE_CHECKING

from .base import EconoInterface

if TYPE_CHECKING:
    from ...core import EconoAgent, EconoDuration, EconoDate, EconoCurrency, EconoInstrument


__all__ = [
    "EconoPayment",
]


class EconoPayment(EconoInterface):
    __slots__ = (
        "_payer",
        "_recipient",
        "_amount_due",
        "_form",
        "_date_due",
        "_window",
        "_date_opened",
        "_date_closed",
        "_amount_paid",
    )
    _payer: EconoAgent
    _recipient: EconoAgent
    _amount_due: EconoCurrency
    _form: type[EconoInstrument]
    _date_due: EconoDate
    _window: EconoDuration
    _date_opened: EconoDate
    _date_closed: EconoDate | None
    _amount_paid: EconoCurrency | None
    
    
    def __init__(
        self,
        payer: EconoAgent,
        recipient: EconoAgent,
        amount: EconoCurrency,
        form: type[EconoInstrument],
        date: EconoDate,
        window: EconoDuration,
    ) -> None:
        self._payer = payer
        self._recipient = recipient
        self._amount_due = amount
        self._form = form
        self._date_due = date
        self._window = window
        self._date_opened = payer.calendar.today()
        
        self._date_closed = None
        self._amount_paid = None
    
    def __repr__(self) -> str:
        status = "paid" if self.completed else "unpaid"
        return (
            f"<{type(self).__name__} from {self.payer} to {self.recipient}"
            f" of {self.amount_due} due on {self.date_due} ({status})"
        )
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def payer(self) -> EconoAgent:
        return self._payer
    
    @property
    def recipient(self) -> EconoAgent:
        return self._recipient
    
    @property
    def amount_due(self) -> EconoCurrency:
        return self._amount_due
    
    @property
    def form(self) -> type[EconoInstrument]:
        return self._form
    
    @property
    def date_due(self) -> EconoDate:
        return self._date_due
    
    @property
    def window(self) -> EconoDuration:
        return self._window
    
    @property
    def date_opened(self) -> EconoDate:
        return self._date_opened
    
    @property
    def date_closed(self) -> EconoDate | None:
        return self._date_closed
    
    @property
    def amount_paid(self) -> EconoCurrency | None:
        return self._amount_paid
    
    
    ##########
    # States #
    ##########
    
    @property
    def open(self) -> bool:
        return not self.closed
    
    @property
    def closed(self) -> bool:
        return self.date_closed is not None
    
    @property
    def due(self) -> bool:
        today = self.payer.calendar.today()
        earliest_date = cast(EconoDate, self.date_due - self.window)
        return self.open and today >= earliest_date
    
    @property
    def overdue(self) -> bool:
        today = self.payer.calendar.today()
        return self.open and today > self.date_due
    
    @property
    def completed(self) -> bool:
        return self.closed and self.amount_paid == self.amount_due
    
    @property
    def defaulted(self) -> bool:
        return self.closed and not self.amount_paid
    
    
    ###########
    # Methods #
    ###########
    
    def _close(self) -> None:
        if not self.closed:
            self._date_closed = self.payer.calendar.today()
    
    def complete(self) -> bool:
        if not self.closed and self.due:
            self._amount_paid = self._amount_due
            self._close()
            return True
        return False
    
    def default(self) -> bool:
        if not self.closed and self.due:
            self._amount_paid = self.payer.Currency(0)
            self._close()
            return True
        return False
