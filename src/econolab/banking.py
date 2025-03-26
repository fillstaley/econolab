"""A banking system
"""


from __future__ import annotations
from collections import defaultdict, deque

from .core import BaseAgent


class Agent(BaseAgent):
    def __init__(self, debt_limit: float | None = 0, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.primary_account: Account | None = None
        self._accounts: list[Account] = []
        self._loans: list[Loan] = []
        
        self.debt_limit = debt_limit
        
        self._open_loan_applications: list[LoanApplication] = []
        self._closed_loan_applications: list[LoanApplication] = []

    ##############
    # Properties #
    ##############

    @property
    def money(self) -> float:
        """The amount of money the agent has."""
        return self.primary_account.balance if self.primary_account else 0
    
    @property
    def reviewed_loan_applications(self) -> list[LoanApplication]:
        return [loan for loan in self._open_loan_applications if loan.date_reviewed]
    
    @property
    def debt_load(self) -> float:
        return sum(loan.principal for loan in self._loans) if self._loans else 0
    
    @property
    def debt_capacity(self) -> float | bool:
        return max(0, self.debt_limit - self.debt_load) if self.debt_limit is not None else True
    
    @property
    def outstanding_debt(self) -> float:
        return sum(l.principal for l in self._loans)

    ############
    # Counters #
    ############

    @property
    def issued_debt(self) -> float:
        """A counter for the money the agent borrows from a bank; reset each step."""
        return self.primary_account.issued_debt if self.primary_account else 0

    @property
    def repaid_debt(self) -> float:
        """A counter for the money the agent repays to a bank; reset each step."""
        return self.primary_account.repaid_debt if self.primary_account else 0
    
    @property
    def income(self) -> float:
        """A counter for the money the agent receives from other agents; reset each step."""
        return self.primary_account.income if self.primary_account else 0

    @property
    def spending(self) -> float:
        """A counter for the money the agent sends to other agents; reset each step."""
        return self.primary_account.spending if self.primary_account else 0

    ###########
    # Methods #
    ###########

    def reset_counters(self) -> None:
        pass
    
    def open_account(self, bank: Bank, initial_deposit: float = 0, overdraft_limit: float | None = 0) -> None:
        account = bank.new_account(self, initial_deposit, overdraft_limit)
        self._accounts.append(account)
        return account

    def close_account(self):
        pass

    def loan_payments_due(self, date: int) -> list[tuple[Loan, Payment]]:
        return [
            (loan, payment)
            for loan in self._loans if loan.payment_due(date)
            for payment in loan.payment_schedule if payment.is_due(date)
        ]

    def give_money(self, other: Agent, amount: float) -> bool:
        # direct the agent's bank to transfer money to the receiver
        # eventually this method should choose a common payment system between
        # the giver and the receiver, but this is moot for now
        success = False
        if other.primary_account:
            success = self.primary_account.bank.transfer_money(self, other, amount)
        return success


class Bank(Agent):
    def __init__(
        self,
        loan_options: list[dict] | None, 
        *args,
        **kwargs
    ) -> None:
        """...

        Parameters
        ----------
        loan_options : list[dict] | None
            The possible loans on offer.
        """
        super().__init__(*args, **kwargs)

        self._account_book: dict[Agent, Account] = {}
        self._loan_book: dict[Agent, list[Loan]] = defaultdict(list)
        
        self._loan_options: list[LoanOption] = []
        if loan_options is not None:
            for loan_option in loan_options:
                self._loan_options.append(LoanOption(bank=self, **loan_option))
        
        self._received_loan_applications: deque[LoanApplication] = deque()
        
        self.primary_account = self.open_account(self)

        self.reserve_bank = None
        self.reserve_account = None

        # Initialize counters
        self._extended_credit: float = 0
        self._redeemed_credit: float = 0
        
    ##############
    # Properties #
    ##############

    @property
    def account_holders(self) -> list[Agent]:
        return list(self._account_book.keys())
    
    ############
    # Counters #
    ############
    
    @property
    def extended_credit(self) -> float:
        return self._extended_credit
    
    @property
    def redeemed_credit(self) -> float:
        return self._redeemed_credit

    ###########
    # Methods #
    ###########

    def reset_counters(self) -> None:
        # first reset the bank's counters
        self._extended_credit = 0
        self._redeemed_credit = 0
        
        # then reset the counters for all the bank's accounts
        for account in self._account_book.values():
            account.reset_counters()
        return super().reset_counters()

    def transfer_money(
        self,
        sender: Agent | Account, 
        receiver: Agent | Account, 
        amount: float,
        spending: bool = True,
        income: bool = True,
        interbank: bool = False
    ) -> bool:
        """Transfers money between accounts.

        Parameters
        ----------
        sender : Agent
            The agent from whom money is being transferred
        receiver : Agent
            The agent to whom money is being transferred
        amount : float
            The amount to be transferred
        spending : bool, optional
            Whether the money being transferred should count as spending by the sender, by default True
        income : bool, optional
            Whether the money being transferred should count as income for the receiver, by default True
        interbank : bool, optional
            ...

        Returns
        -------
        success : bool
            Whether or not the money was successfully transferred
        """
        
        # if interbank is True, we have already performed type checking and should return early
        if interbank:
            receiver.credit(amount, income=income)
            return True
        
        # check if sender is an Agent or an account, extract its default account if it's an Agent
        if isinstance(sender, Agent):
            if (sender_account := sender.primary_account) is None:
                raise ValueError("Sender doesn't have a bank account.")
        elif isinstance(sender, Account):
            sender_account = sender
        else:
            raise ValueError(f"Sender must be an Agent or an Account, got {type(sender).__name__}.")
        
        # check if receiver is an Agent or an account, extract its default account if it's an Agent
        if isinstance(receiver, Agent):
            if (receiver_account := receiver.primary_account) is None:
                raise ValueError("Receiver doesn't have a bank account.")
        elif isinstance(receiver, Account):
            receiver_account = receiver
        else:
            raise ValueError(f"Receiver must be an Agent or an Account, got {type(receiver).__name__}.")
        
        # check that the bank has authority to debit sender_account
        if sender_account.bank is not self:
            raise ValueError(f"Sender account {sender_account} is not maintained by bank {self}.")
        
        # check that the source and target of the transfer are distinct
        if sender_account is receiver_account:
            raise ValueError("Sender and receiver accounts cannot be the same.")
        
        if (receiver_bank := receiver_account.bank) is self:
            if success := sender_account.debit(amount, spending=spending):
                receiver_account.credit(amount, income=income)
        elif (reserve_bank := self.reserve_bank) and reserve_bank is receiver_bank.reserve_bank:
            if success := sender_account.debit(amount, spending=spending):
                reserve_bank.transfer_money(self.reserve_account, receiver_bank.reserve_account, amount)
                receiver_bank.transfer_money(None, receiver_account, amount, income=income, interbank=True)
        else:
            raise ValueError("The receiving account cannot be reached.")
        
        return success

    def new_account(
        self,
        holder: Agent, 
        initial_deposit: float = 0, 
        overdraft_limit: float | None = 0,
    ) -> Account | None:
        if holder not in self.account_holders:
            account = Account(self, holder, initial_deposit, overdraft_limit)
            self._account_book[holder] = account
            return account
    
    def close_account(self, holder: Agent) -> bool:
        pass
    
    def loan_options(self, borrower: Agent) -> list[LoanOption]:
        # returns a list of loans for which the borrower is eligible
        # for now it simply returns the whole list
        return self._loan_options
    
    def new_loan(self, application: LoanApplication, date: int) -> Loan | None:
        if application.approved and not application.issued:
            application.date_issued = date
            
            borrower = application.borrower
            
            loan = Loan(
                bank=self,
                borrower=borrower,
                date_issued=application.date_issued,
                principal=application.principal,
                interest_rate=application.interest_rate,
                term=application.term,
                billing_window=application.billing_window,
            )
            
            self._loan_book[borrower].append(loan)
            self._account_book[borrower].credit(loan.principal, issued_debt=True)
            self._extended_credit += loan.principal
            
            return loan
    
    def process_payment(self, borrower: Agent, amount: float, date: int) -> bool:
        if success := self._account_book[borrower].debit(amount, repaid_debt=True):
            self._redeemed_credit += amount
        return success
    
    def close_loan(self,) -> bool:
        pass


class ReserveBank(Bank):
    def __init__(self, loan_options, *args, **kwargs):
        super().__init__(loan_options, *args, **kwargs)


class Account:
    def __init__(
        self, 
        bank: Bank, 
        holder: Agent, 
        initial_deposit: float = 0, 
        overdraft_limit: float | None = 0,
    ) -> None:
        self.bank = bank
        self.holder = holder

        self.overdraft_limit = overdraft_limit if overdraft_limit is not None else float('inf')

        self._balance = initial_deposit
        
        # Initialize counters
        self._issued_debt: float = 0
        self._repaid_debt: float = 0
        self._income: float = 0
        self._spending: float = 0

    ##############
    # Properties #
    ##############

    @property
    def balance(self) -> float:
        """Returns the account's balance."""
        return self._balance
    
    ############
    # Counters #
    ############

    @property
    def issued_debt(self) -> float:
        """A counter for the money created from a bank loan; reset each step."""
        return self._issued_debt

    @property
    def repaid_debt(self) -> float:
        """A counter for the money destroyed by repaying a loan; reset each step."""
        return self._repaid_debt

    @property
    def income(self) -> float:
        """A counter for the money received from another agent; reset each step."""
        return self._income

    @property
    def spending(self) -> float:
        """A counter for the money sent to another agent; reset each step."""
        return self._spending

    ###########
    # Methods #
    ###########

    def reset_counters(self) -> None:
        self._issued_debt = 0
        self._repaid_debt = 0
        self._income = 0
        self._spending = 0

    def credit(self, amount: float, issued_debt: bool = False, income: bool = True) -> None:
        """Increase the account balance.

        Parameters
        ----------
        amount : float
            The amount by which to increase the account balance
        issued_debt : bool, optional
            The amount is created from issuing debt, by default False
        income : bool, optional
            The amount is transferred from another account, by default True

        """
        self._balance += amount
        if issued_debt:
            self._issued_debt += amount
        elif income:
            self._income += amount

    def debit(self, amount: float, repaid_debt: bool = False, spending: bool = True) -> bool:
        """Attempts to decrease the account balance, respecting overdraft limits.

        Parameters
        ----------
        amount : float
            The amount by which to decrease the account balance.
        repaid_debt : bool, optional
            If True, the amount is destroyed by repaying debt (default: False).
        spending : bool, optional
            If True, the amount is transferred to another account (default: True).
        
        Returns
        -------
        success : bool
            True if the debit operation was successful, False if insufficient funds.
        """

        if success := self._balance - amount + self.overdraft_limit >= 0:
            self._balance -= amount
            if repaid_debt:
                self._repaid_debt += amount
            elif spending:
                self._spending += amount
        return success


class Loan:
    """Creates money."""

    def __init__(
        self,
        bank: Bank,
        borrower: Agent,
        date_issued: int,
        principal: float,
        interest_rate: float = 0.0,
        term: int | None = None,
        billing_window: int = 0,
        payment_schedule: list[Payment] | None = None,
    ) -> None:
        self.bank = bank
        self.borrower = borrower
        self.date_issued = date_issued
        self._principal = principal
        self.interest_rate = interest_rate
        self.term = term
        self.billing_window = billing_window
        
        self.payment_schedule = payment_schedule or [Payment(principal, date_issued + term)]
    
    ##############
    # Properties #
    ##############
    
    @property
    def principal(self) -> float:
        return self._principal
    
    @property
    def due_date(self):
        return self.date_issued + self.term if self.term else None

    @property
    def interest(self):
        return self.principal * self.interest_rate * self.term if self.term else 0

    @property
    def amount_due(self):
        return self.principal + self.interest

    ###########
    # Methods #
    ###########
    
    def capitalize(self, amount: float):
        self._principal += amount
    
    def amortize(self, amount: float):
        self._principal -= amount
    
    def payment_due(self, date: int) -> bool:
        return any(payment.is_due(date) for payment in self.payment_schedule)
    
    def amount_due(self, date: int) -> float:
        return sum(payment.amount_due for payment in self.payment_schedule if payment.is_due(date))
    
    def pay(self, payment: Payment, date: int):
        bank = self.bank
        borrower = self.borrower
        amount = payment.amount_due
        
        if success := bank.process_payment(borrower, amount, date):
            self.amortize(amount)
            payment.mark_paid(amount, date)
        return success


class Payment:
    def __init__(self, amount_due: float, date_due: int, billing_window: int = 0) -> None:
        self.amount_due = amount_due
        self.date_due = date_due
        
        self.billing_window = billing_window
        
        self.amount_paid: float | None = None
        self.date_paid: int | None = None
    
    @property
    def paid(self) -> bool:
        return self.amount_paid is not None
    
    def is_due(self, date) -> bool:
        return not self.paid and date >= self.date_due - self.billing_window
    
    def mark_paid(self, amount_paid: float, date_paid: int) -> None:
        if not self.paid:
            self.amount_paid = amount_paid
            self.date_paid = date_paid


class LoanOption:
    def __init__(
        self,
        bank: Bank,
        term: int, 
        billing_window: int = 0,
        max_principal: float | None = None, 
        min_interest_rate: float = 0,
    ):
        self.bank = bank
        self.term = term
        self.billing_window = billing_window
        self.max_principal = max_principal
        self.min_interest_rate = min_interest_rate
    
    ###########
    # Methods #
    ###########
    
    def apply(self, borrower: Agent, principal: float, date: int) -> LoanApplication:
        if self.max_principal:
            principal = max(principal, self.max_principal)
        
        return LoanApplication(
            bank=self.bank,
            borrower=borrower,
            date_opened=date,
            principal=principal,
            interest_rate=self.min_interest_rate,
            term=self.term,
            billing_window=self.billing_window,
        )


class LoanApplication:
    
    def __init__(self, 
        bank: Bank, 
        borrower: Agent, 
        date_opened: int,
        principal: float, 
        interest_rate: float,
        term: int,
        billing_window: int,
    ):
        self.bank = bank
        self.borrower = borrower
        self.principal = principal
        self.interest_rate = interest_rate
        self.term = term
        self.billing_window = billing_window

        self.date_opened = date_opened
        self.date_reviewed = None
        self.date_closed = None
        self.date_issued = None
        
        self.approved = None
        self.accepted = None
        
        bank._received_loan_applications.append(self)
    
    ##############
    # Properties #
    ##############
    
    @property
    def closed(self) -> bool:
        return self.date_closed is not None
    
    @property
    def issued(self) -> bool:
        return self.date_issued is not None
    
    ###########
    # Methods #
    ###########
    
    def accept(self, date: int) -> Loan | None:
        # a loan should only be issued once
        if self.approved and not self.closed:
            self.date_closed = date

            return self.bank.new_loan(self, date)
