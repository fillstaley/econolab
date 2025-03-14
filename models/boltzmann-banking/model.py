from typing import Any

import numpy as np
import mesa

from econolab import metrics

from agents import Individual, Bank, ReserveBank


class BoltzmannBanking(mesa.Model):
    """The Boltzmann wealth model with a bank"""
    
    def __init__(self,
        num_individuals: int,
        num_banks: int = 1,
        init_gift: float = 0,
        borrowing_limit: float | None = None,
        lending_limit: float | None = None,
        loan_review_limit: int | None = None,
        loan_options: list[dict] | None = None,
        seed: int | None = None,
    ) -> None:
        super().__init__(seed=seed)
        
        # Create individuals
        Individual.create_agents(
            model=self,
            n=num_individuals,
            debt_limit=borrowing_limit,
        )

        loan_options_per_bank = [loan_options for _ in range(num_banks)]

        # Create banks
        Bank.create_agents(
            model=self,
            n=num_banks,
            loan_review_limit=loan_review_limit,
            loan_options=loan_options_per_bank,
        )

        # if there is more than 1 bank, we need to create a reserve bank
        if num_banks > 1:
            ReserveBank.create_agents(
                model=self,
                n=1,
                loan_options=None,
            )
            reserve_bank = self.agents_by_type[ReserveBank][0]
            for b in self.agents_by_type[Bank]:
                b.reserve_account = b.open_account(reserve_bank, overdraft_limit=None)
                b.reserve_bank = reserve_bank

        # Open a transaction account at the bank for each individual
        for i in self.agents_by_type[Individual]:
            bank = self.random.choice(self.agents_by_type[Bank])
            i.primary_account = i.open_account(bank, initial_deposit=init_gift)
        
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Money Supply": "money_supply",
                "Issued Debt": "issued_debt",
                "Repaid Debt": "repaid_debt",
                "Income": "income",
                "Spending": "spending",
                "Individual Wealth Gini": "individual_wealth_gini",
                "Individual Income Gini": "individual_income_gini",
                "Individual Spending Gini": "individual_spending_gini",
            },
            agent_reporters={
                "Money": "money",
                "Issued Debt": "issued_debt",
                "Repaid Debt": "repaid_debt",
                "Income": "income",
                "Spending": "spending",
            },
            agenttype_reporters={
                Individual: {
                    "Wealth": "wealth",
                    "Issued Debt": "issued_debt",
                    "Repaid Debt": "repaid_debt",
                    "Income": "income",
                    "Spending": "spending",
                }
            },
            tables={
                "Individual Wealth Curve": [
                    "Step",
                    "Population Share",
                    "Cumulative Wealth"
                ],
                "Individual Income Curve": [
                    "Step",
                    "Population Share",
                    "Cumulative Income"
                ]
            }
        )
        
        self.datacollector.collect(self)
        self._store_lorenz_wealth_curve()
        self._store_lorenz_income_curve()
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def money_supply(self) -> float:
        return sum(agent.money for agent in self.agents)
    
    @property
    def issued_debt(self) -> float:
        return sum(agent.issued_debt for agent in self.agents)
    
    @property
    def repaid_debt(self) -> float:
        return sum(agent.repaid_debt for agent in self.agents)
    
    @property
    def income(self) -> float:
        return sum(agent.income for agent in self.agents)
    
    @property
    def spending(self) -> float:
        return sum(agent.spending for agent in self.agents)
    
    @property
    def individuals(self):
        return self.agents_by_type[Individual]
    
    @property
    def individual_wealth_data(self) -> list[float]:
        return [i.wealth for i in self.agents_by_type[Individual]]
    
    @property
    def individual_wealth_gini(self) -> float:
        return metrics.gini_index(self.individual_wealth_data)
    
    @property
    def individual_income_data(self) -> float:
        return [i.income for i in self.agents_by_type[Individual]]
    
    @property
    def individual_income_gini(self) -> float:
        return metrics.gini_index(self.individual_income_data)
    
    @property
    def individual_spending_data(self) -> float:
        return [i.spending for i in self.agents_by_type[Individual]]
    
    @property
    def individual_spending_gini(self) -> float:
        return metrics.gini_index(self.individual_spending_data)
    
    @property
    def individual_data(self):
        return self.datacollector.get_agenttype_vars_dataframe(Individual)
    
    ###############
    # Step Method #
    ###############
    
    def step(self):
        """Advances the model by a single step"""

        self.agents.shuffle_do("reset_counters")
        
        self.agents_by_type[Individual].do("act")
        self.agents_by_type[Bank].do("act")

        self.datacollector.collect(self)
        self._store_lorenz_wealth_curve()
        self._store_lorenz_income_curve()
    
    ###########
    # Methods #
    ###########
    
    def lorenz_wealth_values(self, step, p_values):
        
        pop_share, cumulative = self.lorenz_wealth_curve(step)

        indices = np.searchsorted(pop_share, np.array(p_values))
        indices = np.clip(indices, 0, len(cumulative) - 1)  # Ensure indices stays within bounds
        
        return {p: cumulative[idx] for p, idx in zip(p_values, indices)}
    
    def lorenz_wealth_curve(self, step):
        
        table = self.datacollector.get_table_dataframe("Individual Wealth Curve")
        row = table.loc[table["Step"] == step]
        
        if row.empty:
            raise ValueError(f"No Lorenz curve data available for step {step}")
        
        return np.array(row["Population Share"].values[0]), np.array(row["Cumulative Wealth"].values[0])
    
    def _store_lorenz_wealth_curve(self):
        if len(self.individual_wealth_data) > 0:
            cumulative_share, population_share = metrics.lorenz_curve(self.individual_wealth_data)
        else:
            raise RuntimeError("Model has no individuals. Check initialization.")
        
        self.datacollector.add_table_row(
            "Individual Wealth Curve",
            {"Step": self.steps, "Population Share": population_share, "Cumulative Wealth": cumulative_share}
        )

    def lorenz_income_values(self, step, p_values):
        
        pop_share, cumulative = self.lorenz_income_curve(step)

        indices = np.searchsorted(pop_share, np.array(p_values))
        indices = np.clip(indices, 0, len(cumulative) - 1)  # Ensure indices stays within bounds
        
        return {p: cumulative[idx] for p, idx in zip(p_values, indices)}

    def lorenz_income_curve(self, step):
        
        table = self.datacollector.get_table_dataframe("Individual Income Curve")
        row = table.loc[table["Step"] == step]
        
        if row.empty:
            raise ValueError(f"No Lorenz curve data available for step {step}")
        
        return np.array(row["Population Share"].values[0]), np.array(row["Cumulative Income"].values[0])

    def _store_lorenz_income_curve(self):
        if len(self.individual_income_data) > 0:
            cumulative_share, population_share = metrics.lorenz_curve(self.individual_income_data)
        else:
            raise RuntimeError("Model has no individuals. Check initialization.")
        
        self.datacollector.add_table_row(
            "Individual Income Curve",
            {"Step": self.steps, "Population Share": population_share, "Cumulative Income": cumulative_share}
        )
