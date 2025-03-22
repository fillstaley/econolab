
from numbers import Number


class Counters:
    """A collection of counters for an agent."""
    
    def __init__(self):
        self._counter_types: dict[str, type[Number]] = {}
        
        self._daily_counters: dict[str, Number] = {}
        self._weekly_counters: dict[str, Number] = {}
    
    
    @property
    def all(self) -> set[str]:
        """Returns a set of all counter names."""
        return self.daily | self.weekly
    
    @property
    def daily(self) -> set[str]:
        """Returns a set of all daily counter names."""
        return set(self._daily_counters.keys())
    
    @property
    def weekly(self) -> set[str]:
        """Returns a set of all weekly counter names."""
        return set(self._weekly_counters.keys())
    
    
    def reset_daily(self) -> None:
        """Reset all daily counters."""
        for key in self._daily_counters:
            self._daily_counters[key] = 0
    
    def reset_weekly(self) -> None:
        """Reset all weekly counters."""
        for key in self._weekly_counters:
            self._weekly_counters[key] = 0
    
    def add_daily(
        self, 
        name: str, 
        initial_value: Number | None = None,
        counter_type: type[Number] = float
    ) -> None:
        """Add a daily counter to the agent."""
        if not issubclass(counter_type, Number):
            raise ValueError(f"counter_type must be a number; got {counter_type}.")
        
        if initial_value is not None and not isinstance(initial_value, Number):
            raise ValueError(f"initial_value must be a number; got {initial_value}.")
        
        if name in self.all:
            raise ValueError(f"Counter '{name}' already exists.")
        self._counter_types[name] = counter_type
        self._daily_counters[name] = (
            counter_type(initial_value) if initial_value is not None else counter_type(0)
        )
    
    def add_weekly(
        self, 
        name: str, 
        initial_value: Number | None = None,
        counter_type: type[Number] = float
    ) -> None:
        """Add a weekly counter to the agent."""
        if not issubclass(counter_type, Number):
            raise ValueError(f"counter_type must be a number; got {counter_type}.")
        
        if initial_value is not None and not isinstance(initial_value, Number):
            raise ValueError(f"initial_value must be a number; got {initial_value}.")
        
        if name in self.all:
            raise ValueError(f"Counter '{name}' already exists.")
        self._counter_types[name] = counter_type
        self._weekly_counters[name] = (
            counter_type(initial_value) if initial_value is not None else counter_type(0)
        )
    
    def increment(self, name: str, value: Number = 1) -> None:
        """Increment a counter."""
        if name not in self.all:
            raise ValueError(f"Counter '{name}' not found.")
        
        ct = self._counter_types[name]
        if name in self._daily_counters:
            self._daily_counters[name] = ct(self._daily_counters[name] + value)
        elif name in self._weekly_counters:
            self._weekly_counters[name] = ct(self._weekly_counters[name] + value)
    
    
    def __getitem__(self, name: str) -> float:
        if name in self._daily_counters:
            return self._daily_counters[name]
        else:
            raise ValueError(f"Counter '{name}' not found.")
    
    def __repr__(self):
        return (f"Daily Counters: {self._daily_counters}")
