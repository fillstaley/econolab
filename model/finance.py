"""Auxiliary code

"""


from __future__ import annotations
from collections import defaultdict, deque


class Agent:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._account: Account | None = None
        self._loans: list[Loan] = []

        self._outstanding_loan_applications: list = []
        self._approved_loan_applications: list = []
        self._rejected_loan_applications: list = []
        
        # Initialize counters
        self._new_debt: float = 0
        self._repaid_debt: float = 0

    ##############
    # Properties #
    ##############

    @property
    def money(self) -> float:
        """The amount of money the agent has."""
        return self._account.balance if self._account else 0

    @property
    def income(self) -> float:
        """A counter for the money the agent receives from other agents; reset each step."""
        return self._account.income if self._account else 0

    @property
    def spending(self) -> float:
        """A counter for the money the agent sends to other agents; reset each step."""
        return self._account.spending if self._account else 0

    @property
    def new_debt(self) -> float:
        """A counter for the money the agent borrows from a bank; reset each step."""
        return self._new_debt

    @property
    def repaid_debt(self) -> float:
        """A counter for the money the agent repays to a bank; reset each step."""
        return self._repaid_debt

    @property
    def loans_due(self) -> list[Loan] | None:
        return [
            loan
            for loan in self._loans
            if loan.due_date and loan.due_date <= self.model.date
        ] or None

    ###########
    # Methods #
    ###########

    def reset_counters(self) -> None:
        self._new_debt = 0

    def open_account(self, bank: Bank) -> bool:
        if self._account is None:
            self._account = bank.new_account(self)

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

    def borrow_money(self, bank: Bank, amount: float, date: int) -> bool:
        # submits a loan application to a bank
        application = LoanApplication(bank, self, amount)
        if submitted := bank.receive_loan_application(application):
            application.submitted_date = date
            self._outstanding_loan_applications.append(application)
        return submitted
    
    def accept_loan(self, application: LoanApplication) -> bool:
        self._outstanding_loan_applications.remove(application)
        if application.origination_date:
            self._approved_loan_applications.append(application)
            if loan := application.bank.new_loan(application):
                self._loans.append(loan)
                self._new_debt += loan.principal
        else:
            self._rejected_loan_applications.append(application)
            loan = None
        return bool(loan)
    
    def repay_loan(self) -> bool:
        pass


class Bank(Agent):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._account_book: dict[Agent, Account] = {}
        self._loan_book: dict[Agent, list[Loan]] = defaultdict(list)
        self._received_loan_applications: deque[Loan] = deque()
        
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

    def new_account(self, holder: Agent) -> Account | None:
        if holder not in self.account_holders:
            account = Account(self, holder)
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
    
    def receive_loan_application(self, application: LoanApplication) -> bool:
        self._received_loan_applications.append(application)
        return True

    def offer_loan(self, application: LoanApplication, date: int) -> bool:
        application.origination_date = date
        accepted = application.borrower.accept_loan(application)
        return accepted

    def new_loan(self, application: LoanApplication) -> Loan | None:
        loan = None
        # a new loan is created, and the borrower's account is credited, if the
        # application has been approved by the bank and accepted by the borrower
        if application.origination_date is not None:
            loan = Loan(
                self,
                borrower=application.borrower,
                origination_date=application.origination_date,
                principal=application.principal,
                term=application.term,
                interest_rate=application.interest_rate,
            )
            self._loan_book[loan.borrower].append(loan)
            self._account_book[loan.borrower].credit(loan.principal, new_credit=True)
        return loan

    def close_loan(self, loan: Loan) -> bool:
        if success := not loan.amount_due:
            self._loan_book[loan.borrower].remove(loan)
        return success


class Account:
    def __init__(self, bank: Bank, holder: Agent, initial_deposit: float = 0) -> None:
        self.bank = bank
        self.holder = holder

        self._balance = initial_deposit
        
        # Initialize counters
        self._income = 0
        self._spending = 0
        self._new_credit = 0
        self._redeemed_credit = 0

    ##############
    # Properties #
    ##############

    @property
    def balance(self) -> float:
        """Returns the account's balance."""
        return self._balance

    @property
    def income(self) -> float:
        """A counter for the money received from another agent; reset each step."""
        return self._income

    @property
    def spending(self) -> float:
        """A counter for the money sent to another agent; reset each step."""
        return self._spending

    @property
    def new_credit(self) -> float:
        """A counter for the money created from a bank loan; reset each step."""
        return self._new_credit

    @property
    def redeemed_credit(self) -> float:
        """A counter for the money destroyed by repaying a loan; reset each step."""
        return self._redeemed_credit

    ###########
    # Methods #
    ###########

    def reset_counters(self) -> None:
        self._income = 0
        self._spending = 0
        self._new_credit = 0
        self._redeemed_credit = 0

    def credit(self, amount: float, new_credit: bool = False, income: bool = True) -> bool:
        """Increase the account balance.

        Parameters
        ----------
        amount : float
            The amount by which to increase the account balance
        new_credit : bool, optional
            The amount is newly issued credit, by default False
        income : bool, optional
            The amount is transferred from another account, by default True

        """
        # is there ever a reason for this method to fail?
        success = True
        self._balance += amount
        if new_credit:
            self._new_credit += amount
        elif income:
            self._income += amount
        return success

    def debit(self, amount: float, redemption: bool = False, spending: bool = True) -> bool:
        """Decreases the account balance.

        Parameters
        ----------
        amount : float
            The amount by which to decrease the account balance.
        redemption : bool, optional
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
        if redemption:
            self._redeemed_credit += amount
        elif spending:
            self._spending += amount
        return success


class Loan:
    """Creates money."""

    def __init__(
        self,
        bank: Bank,
        borrower: Agent,
        origination_date: int,
        principal: float,
        term: int | None = None,
        interest_rate: float = 0.0,
    ) -> None:
        self.bank = bank
        self.borrower = borrower
        self.origination_date = origination_date
        self.principal = principal
        self.term = term
        self.interest_rate = interest_rate

    @property
    def due_date(self):
        return self.origination_date + self.term if self.term else None

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


class LoanApplication:
    
    def __init__(self, bank: Bank, borrower: Agent, principal: float, term: int | None = None, interest_rate: float = 0.0):
        self.bank = bank
        self.borrower = borrower
        self.principal = principal
        self.term = term
        self.interest_rate = interest_rate

        self.submitted_date = None
        self.reviewed_date = None
        self.origination_date = None
