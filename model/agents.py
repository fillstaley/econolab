from __future__ import annotations

import mesa

from . import finance


class Individual(finance.Agent, mesa.Agent):
    """The fundamental agents of our economy"""
    
    def __init__(self, model, debt_limit: float | None = None):
        super().__init__(model=model)

        self.debt_limit = debt_limit
    
    ##############
    # Properties #
    ##############
    
    @property
    def wealth(self) -> float:
        return self.money
    
    ###########
    # Methods #
    ###########
    
    def act(self):

        date = self.model.steps
        
        # individuals should apply for a loan if they need money and
        # if they are not already borrowing too much money
        gift_amount = 1
        money_demand = max(0, gift_amount - self.money)
        
        debt_outstanding = sum(l.principal for l in self._loans)
        debt_capacity = max(0, self.debt_limit - debt_outstanding)
        
        if money_demand and debt_capacity:
            borrow_amount = min(money_demand, debt_capacity)
            bank = self._account.bank
            self.borrow_money(bank, borrow_amount, date)
        elif not money_demand:
            other = self
            while other is self:
                other = self.random.choice(self.model.agents_by_type[Individual])
            self.give_money(other, gift_amount)


class Bank(finance.Bank, mesa.Agent):
    """The agents that create money."""
    
    def __init__(
        self,
        model,
        loan_review_limit: int | None = None,
        individual_loan_limit: int | None = None,
    ):
        super().__init__(model=model)

        self.loan_review_limit = loan_review_limit
        self.individual_loan_limit = individual_loan_limit
    
    
    ##############
    # Properties #
    ##############
    
    
    ###########
    # Methods #
    ###########

    def reset_counters(self):
        self._loans_reviewed = 0
        return super().reset_counters()
    
    def act(self):
        date = self.model.steps
        
        while self._received_loan_applications and (self.loan_review_limit is None or self._loans_reviewed < self.loan_review_limit):
            application = self._received_loan_applications.popleft()
            if self.approve_loan(application, date):
                self.offer_loan(application, date)
            self._loans_reviewed += 1

    def approve_loan(self, application: finance.LoanApplication, date: int) -> bool:
        application.reviewed_date = date
        borrower = application.borrower
        
        approved = (
            borrower in self.account_holders
            and (
                self.individual_loan_limit is None
                or len(self._loan_book[borrower]) < self.individual_loan_limit
            )
        )
        
        return approved