import pytest

from econolab.core import BaseModel
from econolab.temporal import TemporalStructure, EconoDuration, EconoDate


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


class TestEconoDuration:
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
        assert hasattr(test_model, "EconoDuration")
        assert isinstance(test_model.EconoDuration, type)
        assert issubclass(test_model.EconoDuration, EconoDuration)
        assert test_model.EconoDuration.__name__.startswith(test_model.name)
        assert test_model.EconoDuration._model is test_model
        assert test_model.EconoDuration._model.temporal_structure is ts
    
    def test_duration_construction(self, test_model):
        EconoDuration = test_model.EconoDuration
        duration1 = EconoDuration(1)
        duration2 = EconoDuration(2, 3)
        duration3 = EconoDuration(days=4)
        duration4 = EconoDuration(days=5, weeks=6)
        
        assert isinstance(duration1, EconoDuration)
        assert isinstance(duration2, EconoDuration)
        assert isinstance(duration3, EconoDuration)
        assert isinstance(duration4, EconoDuration)
        assert duration1 is not duration2
    
    def test_duration_exposes_days(self, test_model):
        EconoDuration = test_model.EconoDuration
        duration = EconoDuration(2)

        assert hasattr(duration, "days")
        assert isinstance(duration.days, int)
        assert duration.days == 2

    @pytest.mark.parametrize("days_per_week, days, weeks, expected_days", [
        (7, 1, 2, 15),
        (5, 2, 3, 17),
        (6, 4, 1, 10),
        (10, 3, 0.5, 8),
    ])
    def test_duration_signature(self, create_mock_mesa_model, days_per_week, days, weeks, expected_days):
        MesaModel = create_mock_mesa_model()
        class TestModel(BaseModel, MesaModel):
            temporal_structure = TemporalStructure(
                minyear=1,
                maxyear=9999,
                days_per_week=days_per_week,
                days_per_month=30,
                months_per_year=12,
            )
        model = TestModel()
        EconoDuration = model.EconoDuration
        duration = EconoDuration(days=days, weeks=weeks)
        assert duration.days == expected_days

    def test_duration_string_representation(self, test_model):
        EconoDuration = test_model.EconoDuration
        dur_singular = EconoDuration(1)
        dur_plural = EconoDuration(7)

        assert str(dur_singular) == "1 day"
        assert repr(dur_singular) == "TestModelEconoDuration(days=1)"

        assert str(dur_plural) == "7 days"
        assert repr(dur_plural) == "TestModelEconoDuration(days=7)"
    
    def test_duration_comparison(self, test_model):
        EconoDuration = test_model.EconoDuration
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

    def test_duration_truthiness(self, test_model):
        EconoDuration = test_model.EconoDuration
        
        assert bool(EconoDuration(5))
        assert not bool(EconoDuration(0))
        
        assert EconoDuration(3)
        assert not EconoDuration(0)
    
    @pytest.mark.parametrize("value", [5, -5])
    def test_duration_unary_arithmetic(self, test_model, value):
        EconoDuration = test_model.EconoDuration
        dur = EconoDuration(value)

        # Unary operations: +, -, abs()
        assert (+dur).days == value
        assert (-dur).days == -value
        assert abs(dur).days == abs(value)

    def test_duration_binary_arithmetic(self, test_model):
        EconoDuration = test_model.EconoDuration
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
        assert hasattr(test_model, "EconoDate")
        assert isinstance(test_model.EconoDate, type)
        assert issubclass(test_model.EconoDate, EconoDate)
        assert test_model.EconoDate.__name__.startswith(test_model.name)
        assert test_model.EconoDate._model is test_model
        assert test_model.EconoDate._model.temporal_structure is ts
    
    def test_date_construction(self, test_model):
        EconoDate = test_model.EconoDate
        
        date1 = EconoDate(2001, 2, 3)
        date2 = EconoDate(year=2004, month=5, day=6)
        
        assert isinstance(date1, EconoDate)
        assert isinstance(date2, EconoDate)
        assert date1 is not date2
    
    def test_date_exposes_year_month_day(self, test_model):
        EconoDate = test_model.EconoDate
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

    def test_date_string_representation(self, test_model):
        EconoDate = test_model.EconoDate

        date = EconoDate(2001, 2, 3)
        assert str(date) == "2001-2-3"
        assert repr(date) == "TestModelEconoDate(year=2001, month=2, day=3)"
    
    def test_date_comparisons(self, test_model):
        EconoDate = test_model.EconoDate
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
    
    def test_date_truthiness(self, test_model):
        EconoDate = test_model.EconoDate
        
        assert bool(EconoDate(2001, 2, 3))
        assert EconoDate(2001, 2, 3)
    
    def test_date_arithmetic(self, test_model):
        EconoDate = test_model.EconoDate
        EconoDuration = test_model.EconoDuration
        
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
    
    def test_date_min(self, test_model):
        EconoDate = test_model.EconoDate
        
        mindate = EconoDate.min()
        assert mindate.year == 2000
        assert mindate.month == 1
        assert mindate.day == 1
    
    def test_date_max(self, test_model):
        EconoDate = test_model.EconoDate
        
        maxdate = EconoDate.max()
        assert maxdate.year == 2005
        assert maxdate.month == 12
        assert maxdate.day == 30
    
    @pytest.mark.parametrize("days, expected_date", [
        (1, (2000, 1, 1)),
        (30, (2000, 1, 30)),
        (31, (2000, 2, 1)),
        (360, (2000, 12, 30)),
        (361, (2001, 1, 1)),
    ])
    def test_date_from_days(self, test_model, days, expected_date):
        EconoDate = test_model.EconoDate
        
        result = EconoDate.from_days(days)
        assert isinstance(result, EconoDate)
        assert (result.year, result.month, result.day) == expected_date
    
    @pytest.mark.parametrize("date, expected_days", [
        ((2000, 1, 1), 1),
        ((2000, 1, 30), 30),
        ((2000, 2, 1), 31),
        ((2000, 12, 30), 360),
        ((2001, 1, 1), 361),
    ])
    def test_date_to_days(self, test_model, date, expected_days):
        EconoDate = test_model.EconoDate
        
        result = EconoDate(*date).to_days()
        assert isinstance(result, int)
        assert result == expected_days
    
    @pytest.mark.parametrize("days, date", [
        (1, (2000, 1, 1)),
        (30, (2000, 1, 30)),
        (31, (2000, 2, 1)),
        (360, (2000, 12, 30)),
        (361, (2001, 1, 1)),
    ])
    def test_date_from_to_days_cycle(self, test_model, days, date):
        EconoDate = test_model.EconoDate
        
        date_from_days = EconoDate.from_days(days)
        assert date_from_days.to_days() == days
        
        date_from_date = EconoDate(*date)
        assert date_from_days == date_from_date
        
        days_from_date = date_from_date.to_days()
        assert EconoDate.from_days(days_from_date) == date_from_date
    
    def test_date_replace(self, test_model):
        EconoDate = test_model.EconoDate
        
        date = EconoDate(2001, 2, 3)
        assert date.replace() == EconoDate(2001, 2, 3)
        assert date.replace(year=2002) == EconoDate(2002, 2, 3)
        assert date.replace(month=5) == EconoDate(2001, 5, 3)
        assert date.replace(day=7) == EconoDate(2001, 2, 7)
        assert date.replace(year=2002, month=5, day=7) == EconoDate(2002, 5, 7)
