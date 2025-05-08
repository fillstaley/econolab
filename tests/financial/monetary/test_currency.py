import pytest

from econolab.core import BaseModel
from econolab.financial.monetary import (
    CurrencySpecification,
    EconoCurrency,
    DEFAULT_CURRENCY_SPECIFICATION,
)

@pytest.fixture(params=[
    # full specification
    {
        "code": "USD",
        "symbol": "$",
        "unit_name": "dollar",
        "unit_plural": "dollars",
        "full_name": "US Dollar",
        "precision": 2,
        "symbol_position": "prefix"
    },
    # minimum information
    {
        "code": "EUR",
        "symbol": "€",
        "unit_name": "euro"
    },
    # custom plural
    {
        "code": "CNY",
        "symbol": "¥",
        "unit_name": "yuan",
        "unit_plural": "yuan",
        "full_name": "Chinese Renminbi",
    },
    # custom precision
    {
        "code": "JPY",
        "symbol": "¥",
        "unit_name": "yen",
        "unit_plural": "yen",
        "full_name": "Japanese Yen",
        "precision": 0
    },
    # suffix symbol
    {
        "code": "SEK",
        "symbol": "kr",
        "unit_name": "krona",
        "unit_plural": "kronor",
        "full_name": "Swedish Krona",
        "symbol_position": "suffix"
    }
])
def currency_specs(request):
    return request.param

def test_currency_creation_from_spec(currency_specs):
    try:
        specs = CurrencySpecification(**currency_specs)
        Currency = type(EconoCurrency.__name__, (EconoCurrency,), specs.to_dict())
        Currency(100)
    except Exception as e:
        pytest.fail(f"Currency creation failed with error: {e}")


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
