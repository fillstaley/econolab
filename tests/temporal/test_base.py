import pytest

from econolab.core import BaseModel
from econolab.temporal import TemporalStructure, EconoDuration, EconoDate


@pytest.fixture
def test_model(create_mock_mesa_model):
    MesaModel = create_mock_mesa_model()
    class TestModel(BaseModel, MesaModel):
        temporal_structure = TemporalStructure(
            minyear=2000,
            maxyear=2005,
            days_per_week=7,
            days_per_month=30,
            months_per_year=12,
        )
    return TestModel()


class TestEconoDuration:
    def test_model_binding(self, create_mock_mesa_model):
        MesaModel = create_mock_mesa_model()
        ts = TemporalStructure(
                minyear=2000,
                maxyear=2005,
                days_per_week=7,
                days_per_month=30,
                months_per_year=12
        )
        class TestModel(BaseModel, MesaModel):
            temporal_structure = ts
        test_model = TestModel()
        
        # Ensure that EconoDuration is bound correctly to the model class
        assert hasattr(test_model, "EconoDuration")
        assert isinstance(test_model.EconoDuration, type)
        assert issubclass(test_model.EconoDuration, EconoDuration)
        assert test_model.EconoDuration.__name__.startswith(test_model.name)
        assert test_model.EconoDuration._model is test_model
        assert test_model.EconoDuration._model.temporal_structure is ts

    @pytest.mark.parametrize("days_per_week, days, weeks, expected_days", [
        (7, 1, 2, 15),
        (5, 2, 3, 17),
        (6, 4, 1, 10),
        (10, 3, 0.5, 8),
    ])
    def test_duration_constructor(self, create_mock_mesa_model, days_per_week, days, weeks, expected_days):
        MesaModel = create_mock_mesa_model()
        class TestModel(BaseModel, MesaModel):
            temporal_structure = TemporalStructure(
                minyear=1,
                maxyear=9999,
                days_per_week=days_per_week,
                days_per_month=30,
                months_per_year=12,
            )
        model = TestModel()
        EconoDuration = model.EconoDuration
        duration = EconoDuration(days=days, weeks=weeks)
        assert duration.days == expected_days
    
    def test_duration_exposes_days(self, test_model):
        EconoDuration = test_model.EconoDuration
        dur = EconoDuration(2)

        assert hasattr(dur, "days")
        assert isinstance(dur.days, int)
        assert dur.days == 2

    @pytest.mark.parametrize("value", [5, -5])
    def test_duration_unary_arithmetic(self, test_model, value):
        EconoDuration = test_model.EconoDuration
        dur = EconoDuration(value)

        # Unary operations: +, -, abs()
        assert (+dur).days == value
        assert (-dur).days == -value
        assert abs(dur).days == abs(value)

    def test_duration_binary_arithmetic(self, test_model):
        EconoDuration = test_model.EconoDuration
        dur1 = EconoDuration(5)
        dur2 = EconoDuration(3)

        # Addition and subtraction
        addition = dur1 + dur2
        assert isinstance(addition, EconoDuration)
        assert addition.days == 8

        subtraction = dur1 - dur2
        assert isinstance(subtraction, EconoDuration)
        assert subtraction.days == 2

        # Multiplication
        multiplication_int = dur1 * 2
        assert isinstance(multiplication_int, EconoDuration)
        assert multiplication_int.days == 10

        int_multiplication = 3 * dur1
        assert isinstance(int_multiplication, EconoDuration)
        assert int_multiplication.days == 15

        multiplication_float = dur2 * 2.5
        assert isinstance(multiplication_float, EconoDuration)
        assert multiplication_float.days == 7

        float_multiplication = 3.5 * dur2
        assert isinstance(float_multiplication, EconoDuration)
        assert float_multiplication.days == 10

        # True division
        true_division_duration = dur1 / dur2
        assert isinstance(true_division_duration, float)
        assert true_division_duration == pytest.approx(5 / 3)

        true_division_int = dur1 / 2
        assert isinstance(true_division_int, EconoDuration)
        assert true_division_int.days == 2

        true_division_float = dur2 / 1.5
        assert isinstance(true_division_float, EconoDuration)
        assert true_division_float.days == 2

        # Floor division
        floor_division_duration = dur1 // dur2
        assert isinstance(floor_division_duration, int)
        assert floor_division_duration == 1

        floor_division_int = dur1 // 2
        assert isinstance(floor_division_int, EconoDuration)
        assert floor_division_int.days == 2

        # Modulo operation
        modulo = dur1 % dur2
        assert isinstance(modulo, EconoDuration)
        assert modulo.days == 2

        # Divmod
        quotient, remainder = divmod(dur1, dur2)
        assert isinstance(quotient, int)
        assert quotient == 1
        assert isinstance(remainder, EconoDuration)
        assert remainder.days == 2

    def test_duration_comparison(self, test_model):
        EconoDuration = test_model.EconoDuration
        d1 = EconoDuration(4)
        d2 = EconoDuration(6)

        # Comparison operations: <, >, <=, >=, ==, !=
        assert d1 < d2
        assert d2 > d1
        assert d1 != d2
        assert d1 <= d2
        assert d2 >= d1
        assert d1 == EconoDuration(4)

    def test_duration_truthiness(self, test_model):
        EconoDuration = test_model.EconoDuration
        
        assert bool(EconoDuration(5))
        assert not bool(EconoDuration(0))
        
        assert EconoDuration(3)
        assert not EconoDuration(0)

    def test_duration_string_representation(self, test_model):
        EconoDuration = test_model.EconoDuration
        dur_singular = EconoDuration(1)
        dur_plural = EconoDuration(7)

        assert str(dur_singular) == "1 day"
        assert repr(dur_singular) == "TestModelEconoDuration(days=1)"

        assert str(dur_plural) == "7 days"
        assert repr(dur_plural) == "TestModelEconoDuration(days=7)"

