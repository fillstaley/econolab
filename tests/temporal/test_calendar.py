"""A suite of tests for the EconoCalendar base class.

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
def calendar_cls(model):
    spec = CalendarSpecification()
    return type(
        "EconoCalendar",
        (EconoCalendar,),
        {"model": model, **spec.to_dict()}
    )


@pytest.fixture
def custom_spec():
    return CalendarSpecification(
        days_per_week=5,
        days_per_month=25,
        months_per_year=4,
        start_year=1_000,
        start_month=2,
        start_day=3,
        max_year=1_234,
        steps_to_days=(2,3)
    )


@pytest.fixture
def standard_spec():
    return CalendarSpecification(
        days_per_month=[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
        start_year=2_001,
        start_month=2,
        start_day=3
    )


class TestSpecification:
    def test_initialization(self):
        try:
            CalendarSpecification()
        except Exception as e:
            pytest.fail(f"Null initialization failed with error: {e}")
        
        try:
            CalendarSpecification(
                days_per_week=5,
                days_per_month=25,
                months_per_year=4,
                start_year=1_000,
                start_month=2,
                start_day=3,
                max_year=1_234,
                steps_to_days=(2, 3)
            )
        except Exception as e:
            pytest.fail(f"Initialization failed with error: {e}")
        
        try:
            CalendarSpecification(
                days_per_month=[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
                start_year=2_001,
                start_month=2,
                start_day=3
            )
        except Exception as e:
            pytest.fail(f"Initialization with sequence failed with error: {e}")
    
    @pytest.mark.parametrize("key, value", (
        ("days_per_week", 5),
        ("days_per_month_seq", [25] * 4),
        ("start_year", 1_000),
        ("start_month", 2),
        ("start_day", 3),
        ("max_year", 1_234),
        ("steps_to_days_ratio", EconoCalendar.StepsDaysRatio(2, 3))
    ))
    def test_to_dict(self, custom_spec, key, value):
        try:
            spec_dict = custom_spec.to_dict()
        except Exception as e:
            pytest.fail(f"'to_dict()' method failed with error: {e}")
        
        assert key in spec_dict
        assert spec_dict[key] == value
    
    def test_days_per_month_sequence(self, standard_spec):
        spec_dict = standard_spec.to_dict()
        dpm = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        assert spec_dict["days_per_month_seq"] == dpm


class TestStepsDaysRatio:
    @pytest.mark.parametrize("ratio, steps, days", [
        ((1, 1), 12, 12),
        ((2, 1), 12, 6),
        ((1, 2), 12, 24),
        ((3, 2), 12, 8),
    ])
    def test_to_days(self, ratio, steps, days):
        ratio = EconoCalendar.StepsDaysRatio(*ratio)
        assert ratio.to_days(steps) == days
    
    @pytest.mark.parametrize("ratio, days, steps", [
        ((1, 1), 12, 12),
        ((2, 1), 12, 24),
        ((1, 2), 12,  6),
        ((3, 2), 12, 18),
    ])
    def test_to_steps(self, ratio, days, steps):
        ratio = EconoCalendar.StepsDaysRatio(*ratio)
        assert ratio.to_steps(days) == steps


class TestSubclassCreation:
    def test_from_specs(self, model, custom_spec):
        try:
            type(
                "EconoCalendar",
                (EconoCalendar,),
                {"model": model, **custom_spec.to_dict()}
            )
        except Exception as e:
            pytest.fail(f"Calendar creation failed with error: {e}")
    
    def test_econoduration_binding(self, calendar_cls):
        assert hasattr(calendar_cls, "EconoDuration")
        assert issubclass(calendar_cls.EconoDuration, EconoDuration)
        assert calendar_cls.EconoDuration.EconoCalendar == calendar_cls
    
    def test_econodate_binding(self, calendar_cls):
        assert hasattr(calendar_cls, "EconoDate")
        assert issubclass(calendar_cls.EconoDate, EconoDate)
        assert calendar_cls.EconoDate.EconoCalendar == calendar_cls


class TestSubclassFunctionality:
    @pytest.mark.parametrize("days, weeks, days_expected", [
        (1, 0, 1),
        (2, 3, 2 + 7 * 3),
    ])
    def test_new_duration(self, calendar_cls, days, weeks, days_expected):
        assert hasattr(calendar_cls, "new_duration")
        assert callable(calendar_cls.new_duration)
        
        null_duration = calendar_cls.new_duration()
        assert isinstance(null_duration, EconoDuration)
        assert null_duration.days == 0
        
        short_duration = calendar_cls.new_duration(days)
        assert isinstance(short_duration, EconoDuration)
        assert short_duration.days == days
        
        long_duration = calendar_cls.new_duration(days, weeks=weeks)
        assert isinstance(long_duration, EconoDuration)
        assert long_duration.days == days_expected
    
    @pytest.mark.parametrize("steps", [0, 1, 10, 100])
    def test_new_duration_from_steps(self, calendar_cls, steps):
        duration = calendar_cls.new_duration_from_steps(steps)
        assert isinstance(duration, EconoDuration)
        assert duration.days == steps
    
    @pytest.mark.parametrize("year, month, day", [
        (1, 1, 1),
        (2001, 2, 3)
    ])
    def test_new_date(self, calendar_cls, year, month, day):
        assert hasattr(calendar_cls, "new_date")
        assert callable(calendar_cls.new_date)
        
        date = calendar_cls.new_date(year, month, day)
        assert isinstance(date, EconoDate)
        assert (date.year, date.month, date.day) == (year, month, day)
    
    @pytest.mark.parametrize("steps, date_expected", [
        (0, (1, 1, 1)),
        (1, (1, 1, 2)),
        (28, (1, 2, 1)),
        (28 * 12, (2, 1, 1)),
    ])
    def test_new_date_from_steps(self, calendar_cls, steps, date_expected):
        assert hasattr(calendar_cls, "new_date_from_steps")
        assert callable(calendar_cls.new_date_from_steps)
        
        date = calendar_cls.new_date_from_steps(steps)
        assert isinstance(date, EconoDate)
        assert (date.year, date.month, date.day) == date_expected
    
    @pytest.mark.parametrize("year, month, day", [
        (1, 1, 1),
        (2001, 2, 3),
    ])
    def test_start_date(self, model, year, month, day):
        spec = CalendarSpecification(
            start_year=year,
            start_month=month,
            start_day=day
        )
        Calendar = type(
            "Calendar",
            (EconoCalendar,),
            {"model": model, **spec.to_dict()}
        )
        start_date = Calendar.start_date()
        assert (start_date.year, start_date.month, start_date.day) == (year, month, day)
    
    @pytest.mark.parametrize("steps, date_expected", [
        (0, (1, 1, 1)),
        (1, (1, 1, 2)),
        (28, (1, 2, 1)),
        (28 * 12, (2, 1, 1)),
    ])
    def test_today(self, model, steps, date_expected):
        model.steps = steps
        spec = CalendarSpecification()
        Calendar = type(
            "Calendar",
            (EconoCalendar,),
            {"model": model, **spec.to_dict()}
        )
        
        assert hasattr(Calendar, "today")
        assert callable(Calendar.today)
        
        today = Calendar.today()
        assert isinstance(today, EconoDate)
        assert (today.year, today.month, today.day) == date_expected


class TestInstantiation:
    def test_model_initialization(self, calendar_cls, model):
        try:
            calendar_cls(model)
        except Exception as e:
            pytest.fail(f"Calendar initialization with a model failed with error: {e}")
    
    @pytest.fixture
    def agent(self):
        class Agent:
            unique_id = 1
        return Agent()
    
    def test_agent_initialization(self, calendar_cls, agent):
        try:
            calendar_cls(agent)
        except Exception as e:
            pytest.fail(f"Calendar initialization with an agent failed with error: {e}")
        
