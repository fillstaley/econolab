"""A suite of tests for the EconoDuration and EconoDate base classes.

...

"""

import pytest
from unittest.mock import MagicMock

from econolab.core import (
    EconoCalendar,
    CalendarSpecification,
    EconoDuration,
)


@pytest.fixture()
def model():
    model = MagicMock()
    model.steps = 0
    model.logger = MagicMock()
    return model


@pytest.fixture
def basic_calendar_cls(model):
    spec = CalendarSpecification()
    return type(
        "Calendar", (EconoCalendar,), {"model": model, **spec.to_dict()}
    )


class TestEconoDuration:
    def test_calendar_binding(self, model):
        spec = CalendarSpecification()
        Calendar = type(
            "Calendar", (EconoCalendar,), {"model": model, **spec.to_dict()}
        )
        
        # Ensure that EconoDuration is bound correctly to an EconoCalendar subclass
        assert hasattr(Calendar, "EconoDuration")
        assert issubclass(Calendar.EconoDuration, EconoDuration)
        assert Calendar.EconoDuration.EconoCalendar is Calendar
    
    @pytest.mark.parametrize("days, weeks", [
        (1, 1),
        (2, 3),
    ])
    def test_duration_construction(self, basic_calendar_cls, days, weeks):
        EconoDuration = basic_calendar_cls.EconoDuration
        
        duration1 = EconoDuration(days)
        assert isinstance(duration1, EconoDuration)
        
        duration2 = EconoDuration(days, weeks=weeks)
        assert isinstance(duration2, EconoDuration)
        
        duration3 = EconoDuration(days=days, weeks=weeks)
        assert isinstance(duration3, EconoDuration)
    
    @pytest.mark.parametrize("days_per_week, days, weeks, days_expected", [
        (7, 1, 2, 15),
        (5, 2, 3, 17),
        (6, 4, 1, 10),
        (10, 3, 0.5, 8),
    ])
    def test_duration_exposes_days(self, model, days_per_week, days, weeks, days_expected):
        spec = CalendarSpecification(days_per_week=days_per_week)
        Calendar = type("Calendar", (EconoCalendar,), {"model": model, **spec.to_dict()})
        
        EconoDuration = Calendar.EconoDuration
        duration = EconoDuration(days=days, weeks=weeks)

        assert hasattr(duration, "days")
        assert isinstance(duration.days, int)
        assert duration.days == days_expected

    def test_duration_string(self, basic_calendar_cls):
        EconoDuration = basic_calendar_cls.EconoDuration
        dur_singular = EconoDuration(1)
        dur_plural = EconoDuration(7)

        assert str(dur_singular) == "1 day"

        assert str(dur_plural) == "7 days"
    
    def test_duration_comparison(self, basic_calendar_cls):
        EconoDuration = basic_calendar_cls.EconoDuration
        d1 = EconoDuration(4)
        d2 = EconoDuration(6)

        # check ordering
        assert d1 < d2
        assert d2 > d1
        assert d1 <= d2
        assert d2 >= d1
        
        # check equality
        assert d1 <= d1
        assert d2 >= d2
        assert d1 != d2
        assert d1 == d1
        assert d1 == EconoDuration(4)

    def test_duration_truthiness(self, basic_calendar_cls):
        EconoDuration = basic_calendar_cls.EconoDuration
        
        assert bool(EconoDuration(5))
        assert not bool(EconoDuration(0))
        
        assert EconoDuration(3)
        assert not EconoDuration(0)
    
    @pytest.mark.parametrize("value", [5, -5])
    def test_duration_unary_arithmetic(self, basic_calendar_cls, value):
        EconoDuration = basic_calendar_cls.EconoDuration
        dur = EconoDuration(value)

        # Unary operations: +, -, abs()
        assert (+dur).days == value
        assert (-dur).days == -value
        assert abs(dur).days == abs(value)

    def test_duration_binary_arithmetic(self, basic_calendar_cls):
        EconoDuration = basic_calendar_cls.EconoDuration
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
