"""A suite of tests for the EconoDuration and EconoDate base classes.

...

"""

import pytest
from unittest.mock import MagicMock

from econolab.temporal import (
    EconoCalendar,
    CalendarSpecification,
    EconoDuration,
    EconoDate
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


class TestEconoDate:
    def test_calendar_binding(self, model):
        spec = CalendarSpecification()
        Calendar = type(
            "Calendar", (EconoCalendar,), {"model": model, **spec.to_dict()}
        )
        
        # Ensure that EconoDuration is bound correctly to an EconoCalendar subclass
        assert hasattr(Calendar, "EconoDate")
        assert issubclass(Calendar.EconoDate, EconoDate)
        assert Calendar.EconoDate.EconoCalendar is Calendar
    
    def test_date_construction(self, basic_calendar_cls):
        EconoDate = basic_calendar_cls.EconoDate
        
        date1 = EconoDate(2001, 2, 3)
        date2 = EconoDate(year=2004, month=5, day=6)
        
        assert isinstance(date1, EconoDate)
        assert isinstance(date2, EconoDate)
        assert date1 is not date2
    
    def test_date_exposes_year_month_day(self, basic_calendar_cls):
        EconoDate = basic_calendar_cls.EconoDate
        date = EconoDate(year=2001, month=2, day=3)

        assert hasattr(date, "year")
        assert isinstance(date.year, int)
        assert date.year == 2001

        assert hasattr(date, "month")
        assert isinstance(date.month, int)
        assert date.month == 2

        assert hasattr(date, "day")
        assert isinstance(date.day, int)
        assert date.day == 3

    def test_date_string_representation(self, basic_calendar_cls):
        EconoDate = basic_calendar_cls.EconoDate

        date = EconoDate(2001, 2, 3)
        assert str(date) == "2001-2-3"
    
    def test_date_comparisons(self, basic_calendar_cls):
        EconoDate = basic_calendar_cls.EconoDate
        date1 = EconoDate(2001, 2, 3)
        date2 = EconoDate(2001, 4, 5)

        # check ordering
        assert date1 < date2
        assert date2 > date1
        assert date1 <= date2
        assert date2 >= date1

        # check equality
        assert date1 <= date1
        assert date2 >= date2
        assert date1 != date2
        assert date1 == date1
        assert date1 == EconoDate(2001, 2, 3)
    
    def test_date_truthiness(self, basic_calendar_cls):
        EconoDate = basic_calendar_cls.EconoDate
        
        assert bool(EconoDate(2001, 2, 3))
        assert EconoDate(2001, 2, 3)
    
    def test_date_arithmetic(self, basic_calendar_cls):
        EconoDate = basic_calendar_cls.EconoDate
        EconoDuration = basic_calendar_cls.EconoDuration
        
        date1 = EconoDate(2001, 2, 3)
        date2 = EconoDate(2001, 2, 5)
        duration = EconoDuration(2)
        
        addition_right = date1 + duration
        assert addition_right == date2
        
        addition_left = duration + date1
        assert addition_left == date2
        
        subtraction_date = date2 - date1
        assert subtraction_date == duration
        
        subtraction_duration = date2 - duration
        assert subtraction_duration == date1
    
    def test_date_min(self, basic_calendar_cls):
        EconoDate = basic_calendar_cls.EconoDate
        
        mindate = EconoDate.min()
        assert mindate.year == 1
        assert mindate.month == 1
        assert mindate.day == 1
    
    def test_date_max(self, basic_calendar_cls):
        EconoDate = basic_calendar_cls.EconoDate
        
        maxdate = EconoDate.max()
        assert maxdate.year == 9_999
        assert maxdate.month == 12
        assert maxdate.day == 28
    
    @pytest.mark.parametrize("days, expected_date", [
        (1, (1, 1, 1)),
        (28, (1, 1, 28)),
        (29, (1, 2, 1)),
        (336, (1, 12, 28)),
        (337, (2, 1, 1)),
    ])
    def test_date_from_days(self, basic_calendar_cls, days, expected_date):
        EconoDate = basic_calendar_cls.EconoDate
        
        result = EconoDate.from_days(days)
        assert isinstance(result, EconoDate)
        assert (result.year, result.month, result.day) == expected_date
    
    @pytest.mark.parametrize("date, expected_days", [
        ((1, 1, 1), 1),
        ((1, 1, 28), 28),
        ((1, 2, 1), 29),
        ((1, 12, 28), 336),
        ((2, 1, 1), 337),
    ])
    def test_date_to_days(self, basic_calendar_cls, date, expected_days):
        EconoDate = basic_calendar_cls.EconoDate
        
        result = EconoDate(*date).to_days()
        assert isinstance(result, int)
        assert result == expected_days
    
    @pytest.mark.parametrize("days, date", [
        (1, (1, 1, 1)),
        (28, (1, 1, 28)),
        (29, (1, 2, 1)),
        (336, (1, 12, 28)),
        (337, (2, 1, 1)),
    ])
    def test_date_from_to_days_cycle(self, basic_calendar_cls, days, date):
        EconoDate = basic_calendar_cls.EconoDate
        
        date_from_days = EconoDate.from_days(days)
        assert date_from_days.to_days() == days
        
        date_from_date = EconoDate(*date)
        assert date_from_days == date_from_date
        
        days_from_date = date_from_date.to_days()
        assert EconoDate.from_days(days_from_date) == date_from_date
    
    def test_date_replace(self, basic_calendar_cls):
        EconoDate = basic_calendar_cls.EconoDate
        
        date = EconoDate(2001, 2, 3)
        assert date.replace() == EconoDate(2001, 2, 3)
        assert date.replace(year=2002) == EconoDate(2002, 2, 3)
        assert date.replace(month=5) == EconoDate(2001, 5, 3)
        assert date.replace(day=7) == EconoDate(2001, 2, 7)
        assert date.replace(year=2002, month=5, day=7) == EconoDate(2002, 5, 7)
