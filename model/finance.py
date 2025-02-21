"""Auxiliary code

"""


from __future__ import annotations
from collections import defaultdict, deque


class Agent:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._account: Account | None = None
        self._loans: list[Loan] = []
        
        self._open_loan_applications: list[LoanApplication] = []
        self._closed_loan_applications: list[LoanApplication] = []
        
        self._outstanding_loan_applications: list = []
        self._approved_loan_applications: list = []
        self._denied_loan_applications: list = []

    ##############
    # Properties #
    ##############

    @property
    def money(self) -> float:
        """The amount of money the agent has."""
        return self._account.balance if self._account else 0
    
    @property
    def reviewed_loan_applications(self) -> list[LoanApplication]:
        return [loan for loan in self._open_loan_applications if loan.date_reviewed]
    
    @property
    def debt_owed(self) -> float:
        return sum(loan.principal for loan in self._loans)
    
    @property
    def debt_capacity(self) -> float:
        return max(0, self.debt_limit - self.debt_owed)
    
    @property
    def outstanding_debt(self) -> float:
        return sum(l.principal for l in self._loans)

    @property
    def loans_due(self) -> list[Loan] | None:
        return [
            loan
            for loan in self._loans
            if loan.due_date and loan.due_date <= self.model.date
        ] or None

    ############
    # Counters #
    ############

    @property
    def new_debt(self) -> float:
        """A counter for the money the agent borrows from a bank; reset each step."""
        return self._account.pure_credit if self._account else 0

    @property
    def repaid_debt(self) -> float:
        """A counter for the money the agent repays to a bank; reset each step."""
        return self._account.pure_debit if self._account else 0
    
    @property
    def income(self) -> float:
        """A counter for the money the agent receives from other agents; reset each step."""
        return self._account.income if self._account else 0

    @property
    def spending(self) -> float:
        """A counter for the money the agent sends to other agents; reset each step."""
        return self._account.spending if self._account else 0

    ###########
    # Methods #
    ###########

    def reset_counters(self) -> None:
        pass
    
    def open_account(self, bank: Bank, initial_deposit: float = 0.0) -> bool:
        if self._account is None:
            self._account = bank.new_account(self, initial_deposit)

    def close_account(self):
        pass

    def give_money(self, other: Agent, amount: float) -> bool:
        # direct the agent's bank to transfer money to the receiver
        # eventually this method should choose a common payment system between
        # the giver and the receiver, but this is moot for now
        success = False
        if other._account:
            success = self._account.bank.transfer_money(self, other, amount)
        return success


class Bank(Agent):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._account_book: dict[Agent, Account] = {}
        self._loan_book: dict[Agent, list[Loan]] = defaultdict(list)

        self.loan_options: list[LoanOption] = []
        
        self._received_loan_applications: deque[LoanApplication] = deque()
        
        self.open_account(self)

        # Initialize counters
        
    ##############
    # Properties #
    ##############

    @property
    def account_holders(self) -> list[Agent]:
        return list(self._account_book.keys())

    ###########
    # Methods #
    ###########

    def reset_counters(self) -> None:
        for account in self._account_book.values():
            account.reset_counters()
        return super().reset_counters()

    def new_account(self, holder: Agent, initial_deposit: float = 0.0) -> Account | None:
        if holder not in self.account_holders:
            account = Account(self, holder, initial_deposit)
            self._account_book[holder] = account
            return account
    
    def close_account(self, holder: Agent) -> bool:
        pass

    def transfer_money(self,
            sender: Agent, 
            receiver: Agent, 
            amount: float,
            spending: bool = True,
            income: bool = True,
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

        Returns
        -------
        success : bool
            Whether or not the money was successfully transferred
        """
        success = False
        if sender in self.account_holders and receiver in self.account_holders:
            if success := self._account_book[sender].debit(amount, spending=spending):
                self._account_book[receiver].credit(amount, income=income)
        return success


class Account:
    def __init__(self, bank: Bank, holder: Agent, initial_deposit: float = 0) -> None:
        self.bank = bank
        self.holder = holder

        self._balance = initial_deposit
        
        # Initialize counters
        self._pure_credit: float = 0
        self._pure_debit: float = 0
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
    def pure_credit(self) -> float:
        """A counter for the money created from a bank loan; reset each step."""
        return self._pure_credit

    @property
    def pure_debit(self) -> float:
        """A counter for the money destroyed by repaying a loan; reset each step."""
        return self._pure_debit

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
        self._pure_credit = 0
        self._pure_debit = 0
        self._income = 0
        self._spending = 0

    def credit(self, amount: float, pure_credit: bool = False, income: bool = True) -> bool:
        """Increase the account balance.

        Parameters
        ----------
        amount : float
            The amount by which to increase the account balance
        pure_credit : bool, optional
            The amount is newly issued credit, by default False
        income : bool, optional
            The amount is transferred from another account, by default True

        """
        # is there ever a reason for this method to fail?
        success = True
        self._balance += amount
        if pure_credit:
            self._pure_credit += amount
        elif income:
            self._income += amount
        return success

    def debit(self, amount: float, pure_debit: bool = False, spending: bool = True) -> bool:
        """Decreases the account balance.

        Parameters
        ----------
        amount : float
            The amount by which to decrease the account balance.
        pure_debit : bool, optional
            The amount is redeemed, by default False
        spending : bool, optional
            The amount is transferred to another account, by default True
        
        Returns
        -------
        success :bool

        """
        # this method should limit the extent to which the account can go negative
        success = True
        self._balance -= amount
        if pure_debit:
            self._pure_debit += amount
        elif spending:
            self._spending += amount
        return success


class Loan:
    """Creates money."""

    def __init__(self,
        bank: Bank,
        borrower: Agent,
        date_issued: int,
        principal: float,
        term: int | None = None,
        interest_rate: float = 0.0,
    ) -> None:
        self.bank = bank
        self.borrower = borrower
        self.date_issued = date_issued
        self.principal = principal
        self.term = term
        self.interest_rate = interest_rate

        # the loan creates money by issuing credit
        bank._loan_book[borrower].append(self)
        bank._account_book[borrower].credit(principal, pure_credit=True)

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

    def repay(self) -> bool:
        principal = self.principal
        amount_due = principal + self.interest

        if self.borrower.money >= amount_due:
            success = self.borrower.give_money(self.bank, amount_due, spending=False)
            if success:
                self.principal -= principal
            return success


class LoanOption:
    def __init__(self,
        bank: Bank,
        borrower_type, 
        term: int, 
        max_principal: float | None = None, 
        min_interest_rate: float = 0
    ):
        self.bank = bank
        self.borrower_type = borrower_type
        self.term = term
        self.max_principal = max_principal
        self.min_interest_rate = min_interest_rate

    def apply(self, borrower: Agent, principal: float, date: int) -> LoanApplication:
        if self.max_principal:
            principal = max(principal, self.max_principal)
        
        return LoanApplication(
            bank=self.bank,
            borrower=borrower,
            date_opened=date,
            term=self.term,
            principal=principal,
            interest_rate=self.min_interest_rate,
        )


class LoanApplication:
    
    def __init__(self, 
        bank: Bank, 
        borrower: Agent, 
        date_opened: int,
        term: int, 
        principal: float, 
        interest_rate: float = 0,
    ):
        self.bank = bank
        self.borrower = borrower
        self.term = term
        self.principal = principal
        self.interest_rate = interest_rate

        self.date_opened = date_opened
        self.date_reviewed = None
        self.date_closed = None
        
        self.approved = None
        self.accepted = None
        
        bank._received_loan_applications.append(self)
    
    def accept_loan(self, date: int) -> Loan | None:
        # this method should only do issue a loan once
        if self.date_closed is None:
            self.date_closed = date

            return Loan(
                bank=self.bank,
                borrower=self.borrower,
                date_issued=self.date_closed,
                principal=self.principal,
                term=self.term,
                interest_rate=self.interest_rate,
            )
