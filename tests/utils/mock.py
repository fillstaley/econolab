from random import Random


# mock classes for Mesa.model and Mesa.Agent
class MockModel:
    def __init__(self):
        self.steps = 1
        self.random = Random(12345)


class MockAgent:
    def __init__(self, model: MockModel):
        self.model = model
        self.unique_id = 1
