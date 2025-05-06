import pytest

from econolab.core import BaseModel, CounterCollection
from econolab.temporal import (
    TemporalStructure,
    DEFAULT_TEMPORAL_STRUCTURE,
    EconoCalendar,
    EconoDate,
    EconoDuration,
)


@pytest.fixture
def simple_model(create_mock_mesa_model):
    MesaModel = create_mock_mesa_model()
    class SimpleModel(BaseModel, MesaModel):
        pass
    return SimpleModel()


class TestInitialization:
    def test_name_set_by_default(self, simple_model):
        assert simple_model.name == "SimpleModel"
    
    def test_name_set_by_attribute(self, create_mock_mesa_model):
        MesaModel = create_mock_mesa_model()
        class SimpleModel(BaseModel, MesaModel):
            name = "TestModel"
        model = SimpleModel()
        
        assert model.name == "TestModel"
    
    def test_name_set_by_constructor(self, create_mock_mesa_model):
        MesaModel = create_mock_mesa_model()
        class SimpleModel(BaseModel, MesaModel):
            name = "TestModel"
        model = SimpleModel(name="Test")
        
        assert model.name == "Test"
    
    @pytest.mark.parametrize("raw,expected", [
        (" Test ", "Test"),
        ("Long Name", "LongName"),
        ("\tTabbed\nName ", "TabbedName"),
    ])
    def test__sanitize_name(self, raw, expected):
        assert BaseModel._sanitize_name(raw) == expected

    def test_model_uses_default_temporal_structure(self, simple_model):
        assert simple_model.temporal_structure == DEFAULT_TEMPORAL_STRUCTURE

    def test_model_uses_given_temporal_structure(self, create_mock_mesa_model):
        ts = TemporalStructure(
            minyear=1,
            maxyear=9999,
            days_per_week=7,
            days_per_month=28,
            months_per_year=4
        )
        MesaModel = create_mock_mesa_model()
        class SimpleModel(BaseModel, MesaModel):
            temporal_structure = ts
        model = SimpleModel()
        
        assert model.temporal_structure == ts

    def test__bind_temporal_types(self, simple_model):
        # Ensure that a named subclass of Calendar is bound to the model
        assert hasattr(simple_model, "EconoCalendar")
        assert issubclass(simple_model.EconoCalendar, EconoCalendar)
        assert simple_model.EconoCalendar._model is simple_model

        # Ensure that a named subclass of EconoDate is bound to the model
        assert hasattr(simple_model, "EconoDate")
        assert issubclass(simple_model.EconoDate, EconoDate)
        assert simple_model.EconoDate._model is simple_model
        
        # Ensure that a named subclass of EconoDuration is bound to the model
        assert hasattr(simple_model, "EconoDuration")
        assert issubclass(simple_model.EconoDuration, EconoDuration)
        assert simple_model.EconoDuration._model is simple_model
    
    def test_model_calendar_instance(self, simple_model):
        assert hasattr(simple_model, "calendar")
        assert isinstance(simple_model.calendar, simple_model.EconoCalendar)
        assert simple_model.calendar._model is simple_model
    
    def test_model_counters(self, simple_model):
        assert hasattr(simple_model, "counters")
        assert isinstance(simple_model.counters, CounterCollection)
        assert simple_model.counters.model is simple_model
