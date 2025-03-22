"""A model of random business activity.
"""

import mesa.agent
import numpy as np
import mesa

from econolab import temporal
from econolab import metrics

from agents import Individual, Business, Bank, ReserveBank


class BoltzmannBusiness(mesa.Model):
    """A Mesa model with many individuals and businesses exchanging money.
    """
    
    def __init__(
        self,
        num_individuals: int,
        num_businesses: int,
        num_banks: int = 1,
        init_gift: float = 0,
        seed: int | None = None,
    ) -> None:
        super().__init__(seed=seed)
        
        #######################
        # Initialize calendar #
        #######################
        
        self.calendar = temporal.Calendar()
        
        #########################
        # Initialize employment #
        #########################
        
        self.job_board = []
        
        ###########################
        # Add agents to the model #
        ###########################
        
        # Individuals
        Individual.create_agents(
            model=self,
            n=num_individuals,
            calendar=self.calendar,
        )

        # Businesses
        Business.create_agents(
            model=self,
            n=num_businesses,
            calendar=self.calendar,
        )
        
        # Banks
        loan_options_per_bank = [None for _ in range(num_banks)]
        Bank.create_agents(
            model=self,
            n=num_banks,
            calendar=self.calendar,
            loan_options=loan_options_per_bank
        )
        # if there is more than 1 bank, we need to create a reserve bank
        if num_banks > 1:
            ReserveBank.create_agents(
                model=self,
                n=1,
                calendar=self.calendar,
                loan_options=None,
            )
            for b in self.banks:
                b.reserve_account = b.open_account(self.reserve_bank, overdraft_limit=None)
                b.reserve_bank = self.reserve_bank
        
        ##############################
        # Initialize monetary system #
        ##############################
        
        # Open a transaction account at the bank for each individual
        for i in self.individuals:
            bank = self.random.choice(self.banks)
            i.primary_account = i.open_account(bank, initial_deposit=init_gift)
        
        # Open a transaction account at the bank for each business
        for b in self.businesses:
            bank = self.random.choice(self.banks)
            b.primary_account = b.open_account(bank, initial_deposit=init_gift)
        
        ################################
        # Initialize the datacollector #
        ################################
        
        self.datacollector = mesa.DataCollector(
            model_reporters = {
                "Unemployment Rate": "unemployment_rate",
            },
            agent_reporters=None,
            agenttype_reporters = {
                Individual: {
                    "Number of Jobs": "number_of_jobs",
                }
            },
            tables=None
        )
        
        self.datacollector.collect(self)


    ##############
    # Properties #
    ##############
    
    @property
    def individuals(self) -> mesa.agent.AgentSet:
        return self.agents_by_type[Individual]
    
    @property
    def businesses(self) -> mesa.agent.AgentSet:
        return self.agents_by_type[Business]
    
    @property
    def banks(self) -> mesa.agent.AgentSet:
        return self.agents_by_type[Bank]
    
    @property
    def reserve_bank(self):
        return self.agents_by_type[ReserveBank][0]
    
    @property
    def unemployment_rate(self) -> float:
        total = len(self.individuals)
        unemployed = sum(1 for i in self.individuals if i.number_of_jobs == 0)
        return unemployed / total if total else 0.0
    
    ###############
    # Step Method #
    ###############
    
    def step(self) -> None:
        """Advances the model by a single step"""

        self.agents.shuffle_do("reset_counters")
        
        self.agents_by_type[Individual].do("act")
        self.agents_by_type[Business].do("act")
        self.agents_by_type[Bank].do("act")
        
        self.datacollector.collect(self)