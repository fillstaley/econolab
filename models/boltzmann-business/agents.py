"""...
"""


from __future__ import annotations

import mesa

from econolab import banking

import employment


class Individual(employment.Employee, banking.Agent, mesa.Agent):
    def __init__(self, model, *args, **kwargs) -> None:
        super().__init__(model=model, *args, **kwargs)
    
    
    ##############
    # Properties #
    ##############
    
    
    ##############
    # Act Method #
    ##############
    
    def act(self) -> None:
        pass

    ###########
    # Methods #
    ###########
    
    def reset_counters(self):
        return super().reset_counters()


class Business(employment.Employer, banking.Agent, mesa.Agent):
    def __init__(self, model, *args, **kwargs) -> None:
        super().__init__(model=model, *args, **kwargs)
    
    
    ##############
    # Properties #
    ##############
    
    
    ##############
    # Act Method #
    ##############
    
    def act(self) -> None:
        pass

    ###########
    # Methods #
    ###########
    
    def reset_counters(self):
        return super().reset_counters()


class Bank(banking.Bank, mesa.Agent):
    def __init__(self, model, *args, **kwargs) -> None:
        super().__init__(model=model, *args, **kwargs)


    ##############
    # Properties #
    ##############


    ##############
    # Act Method #
    ##############

    def act(self) -> None:
        pass

    ###########
    # Methods #
    ###########
    
    def reset_counters(self):
        return super().reset_counters()


class ReserveBank(banking.ReserveBank, mesa.Agent):
    def __init__(self, model, *args, **kwargs) -> None:
        super().__init__(model=model, *args, **kwargs)


    ##############
    # Properties #
    ##############


    ##############
    # Act Method #
    ##############

    def act(self) -> None:
        pass

    ###########
    # Methods #
    ###########
    
    def reset_counters(self):
        return super().reset_counters()
