"""A class that specifies the temporal structure of an EconoLab model.
"""


from typing import Protocol, runtime_checkable

from .econodate import EconoDate, EconoDuration


@runtime_checkable
class ABFModel(Protocol):
    steps: int


class Calendar:
    """A class that specifies the temporal structure of an EconoLab model.
    
    Parameters
    ----------
    model : ABFModel
        The model to which this calendar is attached.
    steps_per_day : int, optional
        The number of steps per EconoLab day, by default 1.
    days_per_week : int, optional
        The number of days per EconoLab week, by default 7.
    days_per_month : int, optional
        The number of days per EconoLab month, by default 30.
    months_per_year : int, optional
        The number of months per EconoLab year, by default 12.
    
    Attributes
    ----------
    
    """
    
    ####################
    # Class Attributes #
    ####################
    
    _model: ABFModel | None = None
    _steps_per_day: int = 1
    _days_per_week: int = 7
    _days_per_month: int = 30
    _months_per_year: int = 12
    
    
    ####################
    # Class Properties #
    ####################
    
    @property
    def model(self) -> ABFModel | None:
        return self.__class__._model
    
    @model.setter
    def model(self, value: ABFModel) -> None:
        raise AttributeError("model is read-only. Use Calendar.configure(model) to change it.")
    
    @property
    def steps_per_day(self) -> int:
        return self.__class__._steps_per_day
    
    @steps_per_day.setter
    def steps_per_day(self, value: int) -> None:
        raise AttributeError("steps_per_day is read-only. Use Calendar.configure(steps_per_day) to change it.")
    
    @property
    def days_per_week(self) -> int:
        return self.__class__._days_per_week
    
    @days_per_week.setter
    def days_per_week(self, value: int) -> None:
        raise AttributeError("days_per_week is read-only. Use Calendar.configure(days_per_week) to change it.")
    
    @property
    def days_per_month(self) -> int:
        return self.__class__._days_per_month
    
    @days_per_month.setter
    def days_per_month(self, value: int) -> None:
        raise AttributeError("days_per_month is read-only. Use Calendar.configure(days_per_month) to change it.")
    
    @property
    def months_per_year(self) -> int:
        return self.__class__._months_per_year
    
    @months_per_year.setter
    def months_per_year(self, value: int) -> None:
        raise AttributeError("months_per_year is read-only. Use Calendar.configure(months_per_year) to change it.")
    
    
    #################
    # Class Methods #
    #################
    
    @classmethod
    def configure(cls,
        model: ABFModel,
        steps_per_day: int | None = None,
        days_per_week: int | None = None,
        days_per_month: int | None = None,
        months_per_year: int | None = None,
    ) -> None:
        if not isinstance(model, ABFModel):
            raise ValueError("model must have a 'steps' attribute")
        cls._model = model
        
        if steps_per_day is not None:
            cls.set_steps_per_day(steps_per_day)
        if days_per_week is not None:
            cls.set_days_per_week(days_per_week)
        if days_per_month is not None:
            cls.set_days_per_month(days_per_month)
        if months_per_year is not None:
            cls.set_months_per_year(months_per_year)
    
    @classmethod
    def set_model(cls, model: ABFModel) -> None:
        if not isinstance(model, ABFModel):
            raise ValueError("model must have a 'steps' attribute")
        cls._model = model
    
    @classmethod
    def set_steps_per_day(cls, value: int) -> None:
        if not isinstance(value, int) or value < 1:
            raise ValueError("steps_per_day must be an integer and at least 1")
        cls._steps_per_day = value
    
    @classmethod
    def set_days_per_week(cls, value: int) -> None:
        if not isinstance(value, int) or value < 1:
            raise ValueError("days_per_week must be an integer and at least 1")
        cls._days_per_week = value
    
    @classmethod
    def set_days_per_month(cls, value: int) -> None:
        if not isinstance(value, int) or value < 1:
            raise ValueError("days_per_month must be an integer and at least 1")
        cls._days_per_month = value
    
    @classmethod
    def set_months_per_year(cls, value: int) -> None:
        if not isinstance(value, int) or value < 1:
            raise ValueError("months_per_year must be an integer and at least 1")
        cls._months_per_year = value
    
    @classmethod
    def convert_steps_to_days(cls, steps: int) -> int:
        return 1 + (steps - 1) // cls.steps_per_day
    
    @classmethod
    def new_date(cls, steps: int) -> EconoDate:
        days = cls.convert_steps_to_days(steps)
        year = days // cls.days_per_year
        month = (days % cls.days_per_year) // cls.days_per_month
        day = days % cls.days_per_month
        return EconoDate(year, month, day)
    
    @classmethod
    def new_duration(cls, steps: int) -> EconoDuration:
        days = cls.convert_steps_to_days(steps)
        return EconoDuration(days)
    
    
    ###############
    # Init Method #
    ###############
    
    def __init__(
        self,
    ) -> None:
        if self.__class__._model is None:
            raise RuntimeError("Calendar not configured. Call Calendar.configure(model) before use.")
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def days_per_year(self):
        return self.days_per_month * self.months_per_year
    
    @property
    def days_per_quarter(self):
        return self.days_per_year // 4
    
    
    def new_date(self, steps: int) -> EconoDate:
        return EconoDate(steps)
    
    def new_duration(self, steps: int) -> EconoDuration:
        return EconoDuration(steps)
    
    def current_date(self) -> EconoDate:
        steps = self.model.steps
        return EconoDate(steps)
    
    def convert_steps_to_days(self, steps: int) -> int:
        return steps
    
    def get_current_day(self, steps: int) -> int:
        return self.convert_steps_to_days(steps) % self.days_per_month
    
    def get_current_month(self, steps: int) -> int:
        total_months = self.convert_steps_to_days(steps) // self.days_per_month
        return total_months % self.months_per_year
    
    def get_current_year(self, steps: int) -> int:
        return self.convert_steps_to_days(steps) // self.days_per_year
