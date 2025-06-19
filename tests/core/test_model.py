"""A suite of tests for the EconoModel base class.

...

"""

import pytest

from econolab.core import (
    EconoModel,
    CounterCollection,
    EconoCalendar,
    CalendarSpecification,
    EconoCurrency,
)


@pytest.fixture
def simple_model(create_mock_mesa_model):
    MesaModel = create_mock_mesa_model()
    class SimpleModel(EconoModel, MesaModel):
        pass
    return SimpleModel()


class TestInitialization:
    def test_name_set_by_default(self, simple_model):
        assert simple_model.name == "SimpleModel"
    
    def test_name_set_by_attribute(self, create_mock_mesa_model):
        MesaModel = create_mock_mesa_model()
        class SimpleModel(EconoModel, MesaModel):
            name = "TestModel"
        model = SimpleModel()
        
        assert model.name == "TestModel"
    
    def test_name_set_by_constructor(self, create_mock_mesa_model):
        MesaModel = create_mock_mesa_model()
        class SimpleModel(EconoModel, MesaModel):
            name = "TestModel"
        model = SimpleModel(name="Test")
        
        assert model.name == "Test"
    
    @pytest.mark.parametrize("raw,expected", [
        (" Test ", "Test"),
        ("Long Name", "LongName"),
        ("\tTabbed\nName ", "TabbedName"),
    ])
    def test__sanitize_name(self, raw, expected):
        assert EconoModel._sanitize_name(raw) == expected
    
    def test__init_temporal_system(self, create_mock_mesa_model):
        spec = CalendarSpecification()
        MesaModel = create_mock_mesa_model()
        class SimpleModel(EconoModel, MesaModel):
            pass
        
        simple_model = SimpleModel(calendar_specification=spec)
        assert hasattr(simple_model, "EconoCalendar")
        assert issubclass(simple_model.EconoCalendar, EconoCalendar)
    
    def test__bind_currency_type(self, simple_model):
        assert hasattr(simple_model, "EconoCurrency")
        assert issubclass(simple_model.EconoCurrency, EconoCurrency)
    
    def test_model_calendar_instance(self, simple_model):
        assert hasattr(simple_model, "calendar")
        assert isinstance(simple_model.calendar, simple_model.EconoCalendar)
        assert simple_model.calendar.model is simple_model
    
    def test_model_counters(self, simple_model):
        assert hasattr(simple_model, "counters")
        assert isinstance(simple_model.counters, CounterCollection)
        assert simple_model.counters.model is simple_model


class TestCalendarBinding:
    def test_has_calendar_class(self):
        pass
    
    def test_has_calendar_instance(self):
        pass
