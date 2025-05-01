import pytest

from econolab.core.base_model import BaseModel
from econolab.temporal import TemporalStructure, EconoDate, EconoDuration, Calendar


class DummyModel(BaseModel):
    temporal_structure = TemporalStructure(
        minyear=2020,
        maxyear=2030,
        days_per_week=7,
        days_per_month=30,
        months_per_year=12,
    )
    steps = 1

def test_temporal_types_are_bound():
    model = DummyModel()

    assert hasattr(model, "EconoDate")
    assert hasattr(model, "EconoDuration")
    assert hasattr(model, "Calendar")

    assert issubclass(model.EconoDate, EconoDate)
    assert issubclass(model.EconoDuration, EconoDuration)
    assert issubclass(model.Calendar, Calendar)

    assert model.EconoDate._model is model
    assert model.EconoDuration._model is model
    assert model.Calendar._model is model

def test_temporal_structure_values_are_used():
    model = DummyModel()

    date = model.EconoDate(2025, 4, 15)
    assert date.year == 2025
    assert date.month == 4
    assert date.day == 15

    duration = model.EconoDuration(weeks=2)
    assert duration.days == 14

    days = date.to_days()
    date2 = model.EconoDate.from_days(days)
    assert date2.year == date.year
    assert date2.month == date.month
    assert date2.day == date.day
