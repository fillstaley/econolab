"""A suite of tests for the EconoDuration and EconoDate base classes.

...

"""

import pytest
from unittest.mock import MagicMock

from econolab.core import (
    EconoCalendar,
    CalendarSpecification,
    EconoDate,
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
