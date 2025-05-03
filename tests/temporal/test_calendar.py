import pytest

from econolab.temporal import (
    TemporalStructure,
    EconoCalendar,
    EconoDate,
    EconoDuration
)
from econolab.core import BaseModel


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


def test_model_has_calendar(test_model):
    assert hasattr(test_model, "calendar")


def test_calendar_get_start_date(test_model):
    test_calendar = test_model.calendar
    start_date = test_calendar.get_start_date()
    assert start_date.year == 2000
    assert start_date.month == 1
    assert start_date.day == 1


@pytest.mark.parametrize("start_year, start_month, start_day", [
    (2000, 1, 1),
    (2001, 2, 3),
    (2005, 12, 30)
])
def test_calendar_set_start_date(test_model, start_year, start_month, start_day):
    test_calendar = test_model.calendar
    test_calendar.set_start_date(start_year, start_month, start_day)
    start_date = test_calendar.get_start_date()
    assert start_date.year == start_year
    assert start_date.month == start_month
    assert start_date.day == start_day


def test_calendar_today_method(test_model):
    test_calendar = test_model.calendar
    today = test_calendar.today()
    assert today.year == 2000
    assert today.month == 1
    assert today.day == 1


def test_calendar_advance_day(test_model):
    test_calendar = test_model.calendar
    first_date = test_calendar.today()
    ...


@pytest.mark.parametrize("steps, days, input_steps, expected_days", [
    (1, 1, 12, 12),
    (2, 1, 12, 6),
    (1, 2, 12, 24),
    (3, 2, 12, 8),
])
def test_steps_to_days_conversion(test_model, steps, days, input_steps, expected_days):
    test_calendar = test_model.calendar
    test_calendar.set_steps_days_ratio(steps, days)
    assert test_calendar.convert_steps_to_days(input_steps) == expected_days


def test_new_duration(test_model):
    test_calendar = test_model.calendar
    duration_from_days = test_calendar.new_duration(days=2)
    duration_from_steps = test_calendar.new_duration(steps=3)
    
    assert isinstance(duration_from_days, EconoDuration)
    assert duration_from_days.days == 2
    
    assert isinstance(duration_from_steps, EconoDuration)
    assert duration_from_steps.days == 3


def test_new_date(test_model):
    test_calendar = test_model.calendar
    date = test_calendar.new_date(2001, 2, 3)
    
    assert isinstance(date, EconoDate)
    assert date.year == 2001
    assert date.month == 2
    assert date.day == 3


def test_new_date_from_steps(test_model):
    test_calendar = test_model.calendar
    date_from_steps = test_calendar.new_date(steps=5)
    
    assert isinstance(date_from_steps, EconoDate)
    assert date_from_steps.year == 2000
    assert date_from_steps.month == 1
    assert date_from_steps.day == 6
