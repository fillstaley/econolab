"""A suite of tests for the EconoCalendar base class.

...

"""

import pytest
from unittest.mock import MagicMock

from econolab.temporal.calendar_new import EconoCalendar, CalendarSpecification


@pytest.fixture
def model():
    model = MagicMock()
    model.steps = 0
    model.logger = MagicMock()
    return model


@pytest.fixture
def specification():
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
    def test_to_dict(self, specification, key, value):
        try:
            spec_dict = specification.to_dict()
        except Exception as e:
            pytest.fail(f"'to_dict()' method failed with error: {e}")
        
        assert key in spec_dict
        assert spec_dict[key] == value
    
    def test_days_per_month_sequence(self, standard_spec):
        spec_dict = standard_spec.to_dict()
        dpm = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        assert spec_dict["days_per_month_seq"] == dpm


class TestCreation:
    def test_from_specs(self, model, specification):
        try:
            type("EconoCalendar", (EconoCalendar,), {
                "model": model,
                **specification.to_dict()
            })
        except Exception as e:
            pytest.fail(f"Calendar creation failed with error: {e}")