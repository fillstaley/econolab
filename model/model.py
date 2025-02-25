from typing import Any

import mesa

from .agents import Individual, Bank
from .finance import LoanOption
from .util import gini_index


class BoltzmannBank(mesa.Model):
    """The Boltzmann wealth model with a bank"""
    
    def __init__(self,
        num_individuals: int,
        num_banks: int = 1,
        init_gift: float = 0,
        borrowing_limit: float | None = None,
        lending_limit: float | None = None,
        loan_review_limit: int | None = None,
        loan_options: list[LoanOption] | None = None,
        seed: int | None = None,
    ) -> None:
        super().__init__(seed=seed)
        
        # Create individuals
        Individual.create_agents(
            model=self,
            n=num_individuals,
            debt_limit=borrowing_limit,
        )

        # Create banks
        Bank.create_agents(
            model=self,
            n=num_banks,
            credit_limit=lending_limit,
            loan_review_limit=loan_review_limit,
            loan_options=loan_options,
        )

        # Open a transaction account at the bank for each individual
        for i in self.agents_by_type[Individual]:
            bank = self.random.choice(self.agents_by_type[Bank])
            i.open_account(bank, initial_deposit=init_gift)
        
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Money Supply": "money_supply",
                "New Debt": "new_debt",
                "Repaid Debt": "repaid_debt",
                "Total Income": "total_income",
                "Total Spending": "total_spending",
                "Individual Wealth Gini": "individual_wealth_gini",
                "Individual Income Gini": "individual_income_gini",
                "Individual Spending Gini": "individual_spending_gini",
            },
            agent_reporters={
                "Money": "money",
                "New Debt": "new_debt",
                "Repaid Debt": "repaid_debt",
                "Income": "income",
                "Spending": "spending",
            },
            agenttype_reporters={
                Individual: {
                    "Wealth": "wealth",
                    "New Debt": "new_debt",
                    "Repaid Debt": "repaid_debt",
                    "Income": "income",
                    "Spending": "spending",
                }
            },
            tables=None
        )
        
        self.datacollector.collect(self)
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def money_supply(self) -> float:
        return sum(agent.money for agent in self.agents)
    
    @property
    def new_debt(self) -> float:
        return sum(agent.new_debt for agent in self.agents)
    
    @property
    def repaid_debt(self) -> float:
        return sum(agent.repaid_debt for agent in self.agents)
    
    @property
    def total_income(self) -> float:
        return sum(agent.income for agent in self.agents)
    
    @property
    def total_spending(self) -> float:
        return sum(agent.spending for agent in self.agents)
    
    @property
    def individual_income_curve(self) -> float:
        return sorted([i.income for i in self.agents_by_type[Individual]])
    
    @property
    def individual_income_gini(self) -> float:
        return gini_index(self.individual_income_curve)
    
    @property
    def individual_wealth_curve(self) -> float:
        return sorted([i.wealth for i in self.agents_by_type[Individual]])
    
    @property
    def individual_wealth_gini(self) -> float:
        return gini_index(self.individual_wealth_curve)
    
    @property
    def individual_spending_curve(self) -> float:
        return sorted([i.spending for i in self.agents_by_type[Individual]])
    
    @property
    def individual_spending_gini(self) -> float:
        return gini_index(self.individual_spending_curve)
    
    
    ###############
    # Step Method #
    ###############
    
    def step(self):
        """Advances the model by a single step"""

        self.agents.shuffle_do("reset_counters")
        
        self.agents_by_type[Individual].do("act")
        self.agents_by_type[Bank].do("act")

        self.datacollector.collect(self)
