"""...
"""


from __future__ import annotations

import mesa

from econolab import banking


class Individual(banking.Agent, mesa.Agent):
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
        
        # first, individuals should manage their reviewed loan applications
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
        
        # second, individuals should manage their due, and overdue, loans
        if loan_payments_due := self.loan_payments_due(date=this_step):
            # for now we won't actually sort anything
            sorted_payments = loan_payments_due
            
            for loan, payment in sorted_payments:
                if self.money >= payment.amount_due:
                    loan.pay(payment, this_step)
                else:
                    ...
                    break
        
        # third, individuals should decide if they want to apply for loans
        # they should only apply if they have a demand for money, a capacity
        # to take on my debt, and have no open loan applications
        gift_amount = 1
        money_demand = max(0, gift_amount - self.money)
        
        if money_demand and self.debt_capacity and not self._open_loan_applications:
            borrow_amount = min(money_demand, self.debt_capacity) if self.debt_capacity is not True else money_demand
            
            # this could all be refactored as a banking.Agent method
            # for now, agents can only borrow from their bank
            bank = self.primary_account.bank
            
            # randomly choose a loan on offer for which the individual is eligible
            if eligible_loans := bank.loan_options(self):
                loan_choice = self.random.choice(eligible_loans)
                
                application = loan_choice.apply(self, borrow_amount, this_step)
                self._open_loan_applications.append(application)
        
        
        # fourth, individuals should decide if they want to spend money, ie. give some away
        if self.money >= gift_amount:
            other = self
            while other is self:
                other = self.random.choice(self.model.agents_by_type[Individual])
            self.give_money(other, gift_amount)


class Bank(banking.Bank, mesa.Agent):
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
    
    def eligible_loans(self, borrower) -> list[banking.LoanOption]:
        return []


class ReserveBank(banking.ReserveBank, mesa.Agent):
    def __init__(self, model, *args, **kwargs):
        super().__init__(model=model, *args, **kwargs)
    
    def act(self):
        pass