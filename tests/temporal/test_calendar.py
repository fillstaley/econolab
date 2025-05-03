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


class TestEconoCalendar:
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
        assert hasattr(test_model, "EconoCalendar")
        assert isinstance(test_model.EconoCalendar, type)
        assert issubclass(test_model.EconoCalendar, EconoCalendar)
        assert test_model.EconoCalendar.__name__.startswith(test_model.name)
        assert test_model.EconoCalendar._model is test_model
        assert test_model.EconoCalendar._model.temporal_structure is ts
    
    # TODO: fill in this test
    def test_calendar_construction(self, test_model):
        pass
    
    # TODO: fill in this test
    def test_calendar_exposes_attributes(self, test_model):
        pass

    @pytest.mark.parametrize("steps, days, input_steps, expected_days", [
        (1, 1, 12, 12),
        (2, 1, 12, 6),
        (1, 2, 12, 24),
        (3, 2, 12, 8),
    ])
    def test_steps_to_days_conversion(self, test_model, steps, days, input_steps, expected_days):
        EconoCalendar = test_model.EconoCalendar
        EconoCalendar.set_steps_days_ratio(steps, days)
        assert EconoCalendar.convert_steps_to_days(input_steps) == expected_days

    def test_calendar_get_start_date(self, test_model):
        EconoCalendar = test_model.EconoCalendar
        start_date = EconoCalendar.get_start_date()
        assert start_date.year == 2000
        assert start_date.month == 1
        assert start_date.day == 1

    @pytest.mark.parametrize("start_year, start_month, start_day", [
        (2000, 1, 1),
        (2001, 2, 3),
        (2005, 12, 30)
    ])
    def test_calendar_set_start_date(self, test_model, start_year, start_month, start_day):
        EconoCalendar = test_model.EconoCalendar
        EconoCalendar.set_start_date(start_year, start_month, start_day)
        start_date = EconoCalendar.get_start_date()
        assert start_date.year == start_year
        assert start_date.month == start_month
        assert start_date.day == start_day

    def test_calendar_new_duration(self, test_model):
        EconoCalendar = test_model.EconoCalendar
        duration_from_days = EconoCalendar.new_duration(days=2)
        duration_from_steps = EconoCalendar.new_duration(steps=3)
        
        assert isinstance(duration_from_days, EconoDuration)
        assert duration_from_days.days == 2
        
        assert isinstance(duration_from_steps, EconoDuration)
        assert duration_from_steps.days == 3

    def test_calendar_new_date(self, test_model):
        test_calendar = test_model.calendar
        
        date = test_calendar.new_date(year=2000, month=1, day=6)
        assert isinstance(date, EconoDate)
        assert date.year == 2000
        assert date.month == 1
        assert date.day == 6
        
        date_from_steps = test_calendar.new_date(steps=5)
        assert isinstance(date_from_steps, EconoDate)
        assert date_from_steps.year == date.year
        assert date_from_steps.month == date.month
        assert date_from_steps.day == date.day

    def test_calendar_today(self, test_model):
        EconoCalendar = test_model.EconoCalendar
        today = EconoCalendar.today()
        assert today.year == 2000
        assert today.month == 1
        assert today.day == 1
