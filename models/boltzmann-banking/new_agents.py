"""EconoLab actors for the Boltzmann Banking model.

...

"""


from mesa import Agent

from econolab.financial import lending


class Individual(lending.Borrower, Agent):
    def __init__(
        self,
        model,
        application_limit = None,
        debt_limit = None
    ) -> None:
        super().__init__(
            model=model,
            application_limit=application_limit,
            debt_limit=debt_limit
        )
    
    def act(self) -> None:
        pass


class Bank(lending.Lender, Agent):
    def __init__(
        self,
        model,
        loan_specs = None,
        limit_loan_applications_reviewed = None,
    ) -> None:
        super().__init__(
            model=model,
            loan_specs=loan_specs,
            limit_loan_applications_reviewed=limit_loan_applications_reviewed,
        )
    
    def act(self) -> None:
        pass
