import pytest

from econolab.core import BaseModel
from econolab.financial.monetary import (
    CurrencySpecification,
    EconoCurrency,
    DEFAULT_CURRENCY_SPECIFICATION,
)


class TestCreation:
    @pytest.fixture(params=[
        # full specification
        (
            {
                "code": "USD",
                "symbol": "$",
                "unit_name": "dollar",
                "unit_plural": "dollars",
                "full_name": "US Dollar",
                "precision": 2,
                "symbol_position": "prefix"
            },
            {
                "code": "USD",
                "symbol": "$",
                "unit_name": "dollar",
                "unit_plural": "dollars",
                "full_name": "US Dollar",
                "precision": 2,
                "symbol_position": "prefix"
            }
        ),
        # minimum information
        (
            {
                "code": "EUR",
                "symbol": "€",
                "unit_name": "euro"
            },
            {
                "code": "EUR",
                "symbol": "€",
                "unit_name": "euro",
                "unit_plural": "euros",
                "full_name": "Euro",
                "precision": 2,
                "symbol_position": "prefix"
            }
        ),
        # custom plural
        (
            {
                "code": "CNY",
                "symbol": "¥",
                "unit_name": "yuan",
                "unit_plural": "yuan",
                "full_name": "Chinese Renminbi",
            },
            {
                "code": "CNY",
                "symbol": "¥",
                "unit_name": "yuan",
                "unit_plural": "yuan",
                "full_name": "Chinese Renminbi",
                "precision": 2,
                "symbol_position": "prefix"
            }
        ),
        # custom precision
        (
            {
                "code": "JPY",
                "symbol": "¥",
                "unit_name": "yen",
                "unit_plural": "yen",
                "full_name": "Japanese Yen",
                "precision": 0
            },
            {
                "code": "JPY",
                "symbol": "¥",
                "unit_name": "yen",
                "unit_plural": "yen",
                "full_name": "Japanese Yen",
                "precision": 0,
                "symbol_position": "prefix"
            }
        ),
        # suffix symbol
        (
            {
                "code": "SEK",
                "symbol": "kr",
                "unit_name": "krona",
                "unit_plural": "kronor",
                "full_name": "Swedish Krona",
                "symbol_position": "suffix"
            },
            {
                "code": "SEK",
                "symbol": "kr",
                "unit_name": "krona",
                "unit_plural": "kronor",
                "full_name": "Swedish Krona",
                "precision": 2,
                "symbol_position": "suffix"
            }
        )
    ])
    def currency_data_with_expected(self, request):
        return request.param
    
    def test_currency_from_data(self, currency_data_with_expected):
        currency_data, _ = currency_data_with_expected
        try:
            specs = CurrencySpecification(**currency_data)
            Currency = type(EconoCurrency.__name__, (EconoCurrency,), specs.to_dict())
            instance = Currency(amount=100)
            
            assert isinstance(instance, EconoCurrency)
        except Exception as e:
            pytest.fail(f"Currency creation failed with error: {e}")
    
    def test_specs_default_unit_plural(self, currency_data_with_expected):
        currency_data, expected = currency_data_with_expected
        specs = CurrencySpecification(**currency_data)
        
        assert specs.unit_plural == expected["unit_plural"]
    
    def test_specs_default_full_name(self, currency_data_with_expected):
        currency_data, expected = currency_data_with_expected
        specs = CurrencySpecification(**currency_data)
        
        assert specs.full_name == expected["full_name"]
    
    def test_specs_default_precision(self, currency_data_with_expected):
        currency_data, expected = currency_data_with_expected
        specs = CurrencySpecification(**currency_data)
        
        assert specs.precision == expected["precision"]
    
    def test_specs_default_symbol_position(self, currency_data_with_expected):
        currency_data, expected = currency_data_with_expected
        specs = CurrencySpecification(**currency_data)
        
        assert specs.symbol_position == expected["symbol_position"]


class TestAccess:
    @pytest.fixture
    def currency_instance(self):
        return
    
    def test_amount(self, currency_instance):
        pass

class TestComparisons:
    pass

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
