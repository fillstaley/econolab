from ....utils.mock import MockModel, MockAgent
from econolab.financial import lending


class TestModel(lending.Model, MockModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TestBorrower(lending.Borrower, MockAgent):
    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)

class TestLender(lending.Lender, MockAgent):
    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
