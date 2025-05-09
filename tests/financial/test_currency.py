"""Tests for the EconoCurrency and CurrencySpecification classes.

Covers:
- Structural validation of dynamically created EconoCurrency subclasses
- Instantiability via CurrencySpecification
- Arithmetic correctness is tested separately in TestArithmetic

"""

import pytest

from econolab.financial import EconoCurrency, CurrencySpecification


@pytest.fixture
def create_currency_class():
    def _make(code="USD", symbol="$", unit_name="dollar", **kwargs):
        specs = CurrencySpecification(code, symbol, unit_name, **kwargs)
        return type(EconoCurrency.__name__, (EconoCurrency,), specs.to_dict())
    return _make


@pytest.fixture
def create_currency_instance(create_currency_class):
    Currency = create_currency_class()
    def _make(amount=0):
        return Currency(amount)
    return _make


class TestCreation:
    """Tests that a concrete EconoCurrency subclass can be created.
    
    The EconoCurrency class is in essence abstract. The CurrencySpecification
    class provides an interface for creating concrete subclasses. Its default
    behavior is tested, as is the way it is expected to be used. The expected
    initialization patterns for subclasses is also tested.
    """
    
    def test_currency_from_specs(self):
        try:
            specs = CurrencySpecification(
                code="USD",
                symbol="$",
                unit_name="dollar"
            )
            type(EconoCurrency.__name__, (EconoCurrency,), specs.to_dict())
        except Exception as e:
            pytest.fail(f"Currency creation failed with error: {e}")
    
    def test_null_instantiation(self, create_currency_class):
        Currency = create_currency_class()
        try:
            Currency()
        except Exception as e:
            pytest.fail(
                f"Currency null initialization failed with and error: {e}"
            )
    
    @pytest.mark.parametrize("input", [1, 0.5, 0, -0.5, -1])
    def test_initialization(self, create_currency_class, input):
        Currency = create_currency_class()
        try:
            Currency(input)
        except Exception as e:
            pytest.fail(
                f"Currency initialization failed with error: {e}"
            )
    
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
    """Tests that currency instances have expected attributes and methods."""
    @pytest.fixture
    def currency_1(self, create_currency_instance):
        return create_currency_instance(1)
    
    def test_amount(self, currency_1):
        assert currency_1.amount == 1
        
        with pytest.raises(AttributeError, match="readonly attribute"):
            currency_1.amount = 10
    
    def test_format_with_symbol(self, currency_1, create_currency_class):
        assert currency_1.format_with_symbol() == "$1.00"
        
        SuffixCurrency = create_currency_class(symbol_position="suffix")
        assert SuffixCurrency(1).format_with_symbol() == "1.00 $"
        
    
    def test_format_with_units(self, currency_1, create_currency_instance):
        assert currency_1.format_with_units() == "1.00 dollar"
        
        not_one = 10
        plural_currency = create_currency_instance(not_one)
        assert plural_currency.format_with_units() == f"{not_one:.2f} dollars"


class TestComparisons:
    """Tests that currency instances are comparable, and nonzero ones are truthy."""
    def test_boolean(self, create_currency_instance):
        nonzero_currency = create_currency_instance(1)
        assert nonzero_currency
        
        zero_currency = create_currency_instance()
        assert not zero_currency
    
    def test_equality(self, create_currency_instance):
        this = create_currency_instance(1)
        that = create_currency_instance(1)
        assert this is not that
        assert this == that

        other = create_currency_instance(2)
        assert other != this
    
    @pytest.fixture
    def currency_small(self, create_currency_instance):
        return create_currency_instance(1)
    
    @pytest.fixture
    def currency_large(self, create_currency_instance):
        return create_currency_instance(10)
    
    def test_less_than(self, currency_small, currency_large):
        assert currency_small < currency_large
        assert currency_small <= currency_small
    
    def test_greater_than(self, currency_small, currency_large):
        assert currency_large > currency_small
        assert currency_large >= currency_large


class TestArithmetic:
    """Tests that arithmetic operations can be used with currency instances."""
    def test_addition(self, create_currency_instance):
        left = create_currency_instance(1)
        right = create_currency_instance(2)
        
        _sum = left + right
        assert _sum.amount == 3
    
    def test_subtraction(self, create_currency_instance):
        left = create_currency_instance(1)
        right = create_currency_instance(2)
        
        difference = left - right
        assert difference.amount == -1
    
    @pytest.mark.parametrize("multiplier", [2, 0.5])
    def test_multiplication(self, create_currency_instance, multiplier):
        multiplicand = create_currency_instance(2)
        
        left_product = multiplier * multiplicand
        left_result = multiplier * multiplicand.amount
        assert left_product.amount == pytest.approx(left_result)
        
        right_product = multiplicand * multiplier
        right_result = multiplicand.amount * multiplier
        assert right_product.amount == pytest.approx(right_result)
    
    def test_division_by_currency(self, create_currency_instance):
        dividend = create_currency_instance(1)
        divisor = create_currency_instance(2)
        quotient = dividend / divisor
        assert isinstance(quotient, float)
        assert quotient == pytest.approx(0.5)
    
    @pytest.mark.parametrize("divisor", [2, 0.5])
    def test_division_by_real_number(self, create_currency_instance, divisor):
        dividend = create_currency_instance(1)
        quotient = dividend / divisor
        result = dividend.amount / divisor
        assert isinstance(quotient, type(dividend))
        assert quotient.amount == pytest.approx(result)
    
    def test_floor_division_by_currency(self, create_currency_instance):
        dividend = create_currency_instance(10)
        divisor = create_currency_instance(3)
        quotient = dividend // divisor
        assert isinstance(quotient, float)
        assert quotient == pytest.approx(3)

    @pytest.mark.parametrize("divisor", [2, 3.5])
    def test_floor_division_by_real_number(self, create_currency_instance, divisor):
        dividend = create_currency_instance(10)
        quotient = dividend // divisor
        result = dividend.amount // divisor
        assert isinstance(quotient, type(dividend))
        assert quotient.amount == pytest.approx(result)
    
    def test_mod(self, create_currency_instance):
        dividend = create_currency_instance(10)
        divisor = create_currency_instance(3)
        remainder = dividend % divisor
        assert isinstance(remainder, type(dividend))
        assert remainder.amount == pytest.approx(1)
    
    def test_divmod(self, create_currency_instance):
        dividend = create_currency_instance(10)
        divisor = create_currency_instance(3)
        quotient, remainder = divmod(dividend, divisor)
        assert quotient == pytest.approx(3)
        assert remainder.amount == pytest.approx(1)
    
    @pytest.mark.parametrize("amount", [1, 0, -1])
    def test_unitary_operations(self, create_currency_instance, amount):
        currency = create_currency_instance(amount)
        assert (+currency).amount == pytest.approx(amount)
        assert (-currency).amount == pytest.approx(-amount)
        assert abs(currency).amount == pytest.approx(abs(amount))
