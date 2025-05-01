import pytest

from econolab.temporal import TemporalStructure
from econolab.temporal import Calendar as BaseCalendar, \
                              EconoDate as BaseDate, \
                              EconoDuration as BaseDuration
from econolab.core.base_model import BaseModel


class NoTSModel(BaseModel):
    """Never sets `temporal_structure` → should fail."""
    pass

def test_missing_temporal_structure_raises():
    with pytest.raises(RuntimeError):
        NoTSModel()


class DummyTS(TemporalStructure):
    """A minimal TemporalStructure for testing."""
    def __init__(self):
        # use small, round numbers so tests are easy to reason about
        super().__init__(
            minyear=1,
            maxyear=9999,
            days_per_week=7,
            days_per_month=30,
            months_per_year=12,
        )

class GoodModel(BaseModel):
    temporal_structure = DummyTS()
    steps = 1

def test_temporal_binding_and_calendar():
    m = GoodModel(name="MyTestModel")

    # 1) the three bound classes should exist on the instance
    for attr, Base in (("Calendar", BaseCalendar),
                       ("EconoDate", BaseDate),
                       ("EconoDuration", BaseDuration)):
        Bound = getattr(m, attr)
        # must be a subclass
        assert issubclass(Bound, Base)
        # and must carry a back-pointer to the model
        assert getattr(Bound, "_model") is m

    # 2) `m.calendar` should be an instance of the bound Calendar
    assert isinstance(m.calendar, m.Calendar)
    # that calendar should also point back to `m`
    assert getattr(type(m.calendar), "_model") is m

    # 3) All date objects created by `m.calendar` are the bound date type
    today = m.calendar.get_start_date()
    assert isinstance(today, m.EconoDate)
    assert type(today)._model is m

    # 4) You can create durations and add them
    dur = m.EconoDuration(days=1)
    tomorrow = today + dur
    assert isinstance(tomorrow, m.EconoDate)
    # and rolling over months/years works…
    end_of_month = m.EconoDate(today.year, today.month, m.temporal_structure.days_per_month)
    next_day = end_of_month + dur
    assert next_day.month == today.month % m.temporal_structure.months_per_year + 1

def test_reset_counters_no_error():
    m = GoodModel()
    # if there are any transient counters at all, it shouldn’t crash
    m.reset_counters()
