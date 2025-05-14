"""...

...

"""

from .._instrument import Instrument
from .agents.deposit_holder import DepositHolder
from .agents.depositor import Depositor


class DepositAccount(Instrument):
    issuer: DepositHolder
    debtor: DepositHolder
    creditor: Depositor
