import pytest

from econolab.core import BaseModel
from econolab.financial.monetary import (
    CurrencySpecification,
    EconoCurrency,
    DEFAULT_CURRENCY_SPECIFICATION,
)


def test_currency_creation(create_mock_mesa_model):
    class EconoModel:
        pass
    model = EconoModel
    specs = CurrencySpecification(
        name="US Dollar",
        symbol="$",
        unit_name="dollar",
        unit_plural="dollars",
        precision=2,
        symbol_position="prefix"
    )
    Currency = type(
        EconoCurrency.__name__,
        (EconoCurrency,),
        {
            "_model": model,
            **specs.to_dict()
        }
    )
    
    assert Currency.name == specs.name


class TestArithmetic:
    
    @pytest.fixture
    def create_currency(self):
        pass
    
    def test_addition(self):
        pass
    
    def test_subtraction(self):
        pass
    
    def test_multiplication(self):
        pass
