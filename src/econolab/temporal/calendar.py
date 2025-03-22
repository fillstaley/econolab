"""A class that specifies the temporal structure of an EconoLab model.
"""


class Calendar:
    def __init__(
        self,
        days_per_week: int = 7,
        days_per_month: int = 30,
    ) -> None:
        self.days_per_week = days_per_week
        self.days_per_month = days_per_month
        
        self.months_per_year = 12
    
    @property
    def days_per_year(self):
        return self.days_per_month * self.months_per_year
    
    @property
    def days_per_quarter(self):
        return self.days_per_year // 4
    
    
    def convert_steps_to_days(self, steps: int) -> int:
        return steps
    
    def get_current_day(self, steps: int) -> int:
        return self.convert_steps_to_days(steps) % self.days_per_month
    
    def get_current_month(self, steps: int) -> int:
        total_months = self.convert_steps_to_days(steps) // self.days_per_month
        return total_months % self.months_per_year
    
    def get_current_year(self, steps: int) -> int:
        return self.convert_steps_to_days(steps) // self.days_per_year
