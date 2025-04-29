"""The Boltzmann Banking Model

...

"""

from mesa import Model

from econolab.financial import lending

from new_agents import Individual, Bank


class BoltzmannBanking(lending.Model, Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        Individual.create_agents(self, 1)
