"""A class that specifies the temporal structure of an EconoLab model.
"""


import logging
logger = logging.getLogger(__name__)

import math
from typing import Protocol, runtime_checkable

from .econodate import EconoDate, EconoDuration



@runtime_checkable
class ABFModel(Protocol):
    steps: int


@runtime_checkable
class ABFAgent(Protocol):
    model: ABFModel


class Calendar:
    """A class that specifies the temporal structure of an EconoLab model.
    """
    
    ####################
    # Class Attributes #
    ####################
    
    _step_units: int = 1
    _day_units: int = 1
    _start_year: int = 1
    _start_month: int = 1
    _start_day: int = 1
    
    
    ####################
    # Class Properties #
    ####################
    
    @property
    def step_units(self) -> int:
        return self.__class__._step_units
    
    @step_units.setter
    def step_units(self, value: int) -> None:
        raise AttributeError("Attribute 'step_units' is readonly. Use Calendar.set_steps_days_ratio() to change it.")
    
    @property
    def day_units(self) -> int:
        return self.__class__._day_units
    
    @day_units.setter
    def day_units(self, value: int) -> None:
        raise AttributeError("Attribute 'day_units' is readonly. Use Calendar.set_steps_days_ratio() to change it.")
    
    @property
    def start_year(self) -> int:
        return self.__class__._start_year
    
    @start_year.setter
    def start_year(self, value: int) -> None:
        raise AttributeError("Attribute 'start_year' is readonly. Use Calendar.set_start_date(year, month, day) to change it.")
    
    @property
    def start_month(self) -> int:
        return self.__class__._start_month
    
    @start_month.setter
    def start_month(self, value: int) -> None:
        raise AttributeError("Attribute 'start_month' is readonly. Use Calendar.set_start_date(year, month, day) to change it.")
    
    @property
    def start_day(self) -> int:
        return self.__class__._start_day
    
    @start_day.setter
    def start_day(self, value: int) -> None:
        raise AttributeError("Attribute 'start_day' is readonly. Use Calendar.set_start_date(year, month, day) to change it.")
    
    @property
    def start_date(self) -> EconoDate:
        return self.__class__.get_start_date()
    
    @start_date.setter
    def start_date(self, value: EconoDate) -> None:
        raise AttributeError("Attribute 'start_date' is readonly. Use Calendar.set_start_date(year, month, day) to change it.")
    
    
    #################
    # Class Methods #
    #################
    
    @classmethod
    def set_steps_days_ratio(cls, steps: int, days: int) -> None:
        """Set the ratio of steps to days.
        
        This method sets the ratio of steps to days. The ratio is used to convert between
        the number of steps and the number of days since the start of the simulation.
        The ratio will be reduced to lowest terms by dividing both by their GCD if
        they are not relatively prime.
        
        Parameters
        ----------
        steps : int
            The number of steps that correspond to the given number of days
        days : int
            The number of days that correspond to the given number of steps
        
        Raises
        ------
        ValueError
            If both steps and days are not integers or either are less than 1
        
        Examples
        --------
        >>> Calendar.set_steps_days_ratio(1, 1)
        >>> EconoDate.new_date(steps=12)
        EconoDate(1, 1, 13)
        >>> Calendar.set_steps_days_ratio(2, 1)
        >>> EconoDate.new_date(steps=12)
        EconoDate(1, 1, 7)
        >>> Calendar.set_steps_days_ratio(1, 2)
        >>> EconoDate.new_date(steps=12)
        EconoDate(1, 1, 25)
        >>> Calendar.set_steps_days_ratio(3, 2)
        >>> EconoDate.new_date(steps=12)
        EconoDate(1, 1, 9)
        
        """
        if not isinstance(steps, int) or steps < 1:
            raise ValueError("'steps' must be an integer and at least 1")
        if not isinstance(days, int) or days < 1:
            raise ValueError("'days' must be an integer and at least 1")
        
        if (gcd := math.gcd(steps, days)) != 1:
            steps, days = steps // gcd, days // gcd
            logger.debug("'steps' and 'days' were not relatively prime; divided both by their GCD (%s)", gcd)
        
        cls._step_units, cls._day_units = steps, days
        logger.info(
            "Updated steps-to-days ratio; now %s equals %s",
            f"{steps} step" if steps == 1 else f"{steps} steps",
            f"{days} day" if days == 1 else f"{days} days",
        )
    
    @classmethod
    def set_start_date(cls, year: int, month: int, day: int) -> None:
        """Set the start date of the simulation.
        
        This method sets the start date of the simulation. The start date is used to
        calculate the number of days since the start of the simulation.
        
        Parameters
        ----------
        year : int
            The year of the start date
        month : int
            The month of the start date
        day : int
            The day of the start date
        
        Raises
        ------
        ValueError
            If year, month, or day are not integers or are less than 1
            If month is not between 1 and 12
            If day is not between 1 and 31
        
        Examples
        --------
        >>> Calendar.set_start_date(1, 1, 1) #default value
        >>> EconoDate.new_date(steps=12)
        EconoDate(1, 1, 13)
        >>> Calendar.set_start_date(2025, 2, 3)
        >>> EconoDate.new_date(steps=12)
        EconoDate(2025, 2, 15)
        
        """
        
        if not isinstance(year, int) or year < 1:
            raise ValueError("'year' must be an integer and at least 1")
        if not isinstance(month, int) or month < 1 or month > 12:
            raise ValueError("'month' must be an integer between 1 and 12")
        if not isinstance(day, int) or day < 1 or day > 31:
            raise ValueError("'day' must be an integer between 1 and 31")
        
        cls._start_year, cls._start_month, cls._start_day = year, month, day
        logger.info("Updated start date; now the calendar begins on year %s", cls.get_start_date())
    
    @classmethod
    def convert_steps_to_days(cls, steps: int) -> int:
        """Convert the number of steps to the number of days since the start of the simulation.
        
        Parameters
        ----------
        steps : int
            The number of steps since the start of the simulation
        
        Returns
        -------
        int
            The number of days since the start of the simulation
        
        Examples
        --------
        >>> Calendar.set_steps_days_ratio(1, 1) # default ratio
        >>> Calendar.convert_steps_to_days(12)
        12
        >>> Calendar.set_steps_days_ratio(2, 1)
        >>> Calendar.convert_steps_to_days(12)
        6
        >>> Calendar.set_steps_days_ratio(1, 2)
        >>> Calendar.convert_steps_to_days(12)
        24
        >>> Calendar.set_steps_days_ratio(3, 2)
        >>> Calendar.convert_steps_to_days(12)
        8
        
        """
        
        return steps * cls._day_units // cls._step_units
    
    @classmethod
    def get_start_date(cls) -> EconoDate:
        return cls.new_date(cls._start_year, cls._start_month, cls._start_day)
    
    @classmethod
    def new_date(
        cls,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
        *,
        steps: int | None = None,
    ) -> EconoDate:
        """Create a new EconoDate object.
        
        This method can be used to create a new EconoDate object in one of two ways:
        
        1. By providing the year, month, and day as integers.
        2. By providing the number of steps since the start of the simulation.
        
        If the number of steps is provided, they must be explicitly passed as a keyword
        argument. In which case, any arguments for year, month, and day will be ignored.
        Otherwise, the year, month, and day must all be provided.
        
        Parameters
        ----------
        year : int, optional
            The year of the date, by default None
        month : int, optional
            The month of the date, by default None
        day : int, optional
            The day of the date, by default None
        steps : int, optional
            The number of steps since the start of the simulation, by default None
        
        Returns
        -------
        EconoDate
            A new EconoDate object, if 'steps' is provided it is relative to `cls.start_date`
        
        Raises
        ------
        ValueError
            If year, month, and day are not all provided
        
        
        Examples
        --------
        >>> Calendar.new_date(2021, 1, 1)
        EconoDate(2021, 1, 1)
        >>> Calendar.set_steps_days_ratio(1, 1) # default ratio
        >>> Calendar.new_date(steps=12)
        EconoDate(1, 1, 13)
        >>> Calendar.set_steps_days_ratio(2, 1)
        >>> Calendar.new_date(steps=12)
        EconoDate(1, 1, 7)
        >>> Calendar.set_steps_days_ratio(1, 2)
        >>> Calendar.new_date(steps=12)
        EconoDate(1, 1, 25)
        >>> Calendar.set_steps_days_ratio(3, 2)
        >>> Calendar.new_date(steps=12)
        EconoDate(1, 1, 9)
        
        """
        
        if steps is not None:
            return cls.get_start_date() + EconoDuration(cls.convert_steps_to_days(steps))
        if year is None or month is None or day is None:
            raise ValueError("year, month, and day must be provided")
        
        return EconoDate(year, month, day)
    
    @classmethod
    def new_duration(cls, days: int = 0, *, steps: int = 0) -> EconoDuration:
        """Create a new EconoDuration object.
        
        This method can be used to create a new EconoDuration object in one of two ways:
        
        1. By providing the number of days as an integer.
        2. By providing the number of steps since the start of the simulation.
        
        If the number of steps is provided, they must be explicitly passed as a keyword
        argument. In which case, the days argument will be ignored. Otherwise, the days
        argument is used, which defaults to 0.

        Parameters
        ----------
        days : int, optional
            The number of days, by default 0
        steps : int, optional
            The number of steps since the start of the simulation, by default 0

        Returns
        -------
        EconoDuration
            A new EconoDuration object
        
        Examples
        --------
        >>> Calendar.new_duration(45)
        EconoDuration(45)
        >>> Calendar.set_steps_days_ratio(3, 2)
        >>> Calendar.new_duration(steps=15)
        EconoDuration(10)
        
        """
        
        if steps:
            return EconoDuration(cls.convert_steps_to_days(steps))
        return EconoDuration(days)
    
    
    ###############
    # Init Method #
    ###############
    
    def __init__(
        self,
        owner: ABFModel | ABFAgent,
    ) -> None:
        if not isinstance(owner, ABFModel) and not isinstance(owner, ABFAgent):
            raise TypeError("Calendar 'owner' must be a valid model or agent object")
        
        self.model = owner if isinstance(owner, ABFModel) else owner.model
        self.agent = owner if isinstance(owner, ABFAgent) else None
        
        logger.debug(
            "New calendar created; it belongs to %s",
            f"agent #{self.agent.unique_id}" if self.agent else f"the model {self.model}"
        )
    
    ###########
    # Methods #
    ###########
    
    def today(self) -> EconoDate:
        """The current date in the simulation, relative to the start date.
        
        Returns
        -------
        EconoDate
            The date in the simulation assuming that step 0 is the start date
        
        Examples
        --------
        >>> Calendar.set_steps_days_ratio(1, 1) # default ratio
        >>> Calendar.set_start_date(1, 1, 1) # default start date
        >>> model.calendar.today()
        EconoDate(1, 1, 1)
        >>> for _ range(100):
        >>>     model.step()
        >>> model.calendar.today
        EconoDate(1, 4, 11) # assuming 30 days per month
        
        """
        
        return self.new_date(steps=self.model.steps)
