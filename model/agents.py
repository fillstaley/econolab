from __future__ import annotations

import mesa

from . import finance


class Individual(finance.Agent, mesa.Agent):
    """The fundamental agents of our economy"""
    
    def __init__(
        self,
        model,
        debt_limit: float | None,
    ):
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

        this_step = self.model.steps

        # first, individuals should manage their open loan applications
        if reviewed_loan_applications := self.reviewed_loan_applications:
            while reviewed_loan_applications:
                loan_application = reviewed_loan_applications.pop(0)
                if loan_application.approved:
                    # for now, applications will be accepted as long as the resulting
                    # amount borrowed is less than the agent's borrowing limit
                    loan_application.accepted = loan_application.principal <= self.debt_capacity
                    if loan_application.accepted:
                        loan = loan_application.accept(this_step)
                        self._loans.append(loan)
                
                self._open_loan_applications.remove(loan_application)
                self._closed_loan_applications.append(loan_application)
        
        
        # individuals should apply for a loan if they need money and
        # if they are not already borrowing too much money
        gift_amount = 1
        money_demand = max(0, gift_amount - self.money)
        
        ## if they want to and can borrow money, then they submit an application
        if money_demand:
            if self.debt_capacity:
                borrow_amount = min(money_demand, self.debt_capacity) if self.debt_capacity is not True else money_demand
                
                # this could all be refactored as a finance.Agent method
                # for now, agents can only borrow from their bank
                bank = self._account.bank
                
                # randomly choose a loan on offer for which the individual is eligible
                if eligible_loans := bank.loan_options(self):
                    loan_choice = self.random.choice(eligible_loans)
                    
                    application = loan_choice.apply(bank, self, borrow_amount, this_step)
                    self._open_loan_applications.append(application)
        else:
            other = self
            while other is self:
                other = self.random.choice(self.model.agents_by_type[Individual])
            self.give_money(other, gift_amount)


class Bank(finance.Bank, mesa.Agent):
    """The agents that create money."""
    
    def __init__(
        self,
        model,
        loan_review_limit: int | None,
        *args,
        **kwargs
    ):
        super().__init__(model=model, *args, **kwargs)
        
        self.loan_review_limit = loan_review_limit
    
    
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
        this_step = self.model.steps
        
        # all banks do for now is review loan applications, which they accept as long as
        # the borrower has not exceeded the bank's lending limit
        while self._received_loan_applications and (self.loan_review_limit is None or self._loans_reviewed < self.loan_review_limit):
            application = self._received_loan_applications.popleft()
            self._loans_reviewed += 1
            
            # for now, all applications are approved
            application.approved = True
            application.date_reviewed = this_step
    
    def eligible_loans(self, borrower) -> list[finance.LoanOption]:
        return []