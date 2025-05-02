import pytest

from typing import Callable


class MockMesaModel:
    steps = 0

@pytest.fixture(autouse=True)
def create_mock_mesa_model() -> Callable[[int], type[MockMesaModel]]:
    def _factory(steps: int = 0) -> type[MockMesaModel]:
        return type(
            "MockMesaModel",
            (MockMesaModel,),
            {"steps": steps}
        )
    return _factory
