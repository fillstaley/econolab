"""A model of random business activity.
"""

import mesa.agent
import numpy as np
import mesa

from econolab import metrics

from agents import Individual, Business, Bank, ReserveBank


class BoltzmannBusiness(mesa.Model):
    """A Mesa model with many individuals and businesses exchanging money.
    """
    
    def __init__(
        self,
        num_individuals: int,
        num_business: int,
        num_banks: int = 1,
        init_gift: float = 0,
        seed: int | None = None,
    ) -> None:
        
        super().__init__(seed=seed)
        
        ###########################
        # Add agents to the model #
        ###########################
        
        # Individuals
        Individual.create_agents(
            model=self,
            n=num_individuals,
        )

        # Businesses
        Business.create_agents(
            model=self,
            n=num_business,
        )
        
        # Banks
        loan_options_per_bank = [None for _ in range(num_banks)]
        Bank.create_agents(
            model=self,
            n=num_banks,
            loan_options=loan_options_per_bank
        )
        # if there is more than 1 bank, we need to create a reserve bank
        if num_banks > 1:
            ReserveBank.create_agents(
                model=self,
                n=1,
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
        
        #########################
        # Initialize employment #
        #########################
        
        
        ################################
        # Initialize the datacollector #
        ################################
        
        self.datacollector = mesa.DataCollector(
            model_reporters=None,
            agent_reporters=None,
            agenttype_reporters=None,
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