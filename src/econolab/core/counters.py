"""...
"""


from numbers import Number
from typing import Protocol, runtime_checkable


@runtime_checkable
class ABFModel(Protocol):
    pass


@runtime_checkable
class ABFAgent(Protocol):
    model: ABFModel


class Counters:
    """A collection of counters for an agent.
    """
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def validate_names(
        counter_types: set[str],
        manual: set[str],
        daily: set[str],
        weekly: set[str],
        monthly: set[str],
        yearly: set[str],
    ) -> None:
        """Validate that counter keys are unique across groups and match counter_types."""
        # Check that there are no overlaps between any groups:
        groups = {
            "manual": manual,
            "daily": daily,
            "weekly": weekly,
            "monthly": monthly,
            "yearly": yearly,
        }
        group_names = list(groups.keys())
        for i in range(len(group_names)):
            for j in range(i + 1, len(group_names)):
                common = groups[group_names[i]] & groups[group_names[j]]
                if common:
                    raise ValueError(
                        f"Duplicate counter names found in groups '{group_names[i]}' and "
                        f"'{group_names[j]}': {common}"
                    )
        
        # Combine all keys and compare with counter_types keys:
        counters = monthly | daily | weekly | monthly | yearly
        if counters != counter_types:
            missing = counter_types - counters
            extra = counters - counter_types
            msg = "Inconsistent counter keys:"
            if missing:
                msg += f" missing {missing}"
            if extra:
                msg += f" extra {extra}"
            raise ValueError(msg)
    
    
    ###################
    # Special Methods #
    ###################
    
    def __getitem__(self, name: str) -> float:
        if name in self._manual_counters:
            return self._manual_counters[name]
        if name in self._daily_counters:
            return self._daily_counters[name]
        elif name in self._weekly_counters:
            return self._weekly_counters[name]
        elif name in self._monthly_counters:
            return self._monthly_counters[name]
        elif name in self._yearly_counters:
            return self._yearly_counters[name]
        else:
            raise ValueError(f"Counter '{name}' not found.")
    
    def __init__(
        self,
        owner: ABFModel | ABFAgent,
        counter_types: dict[str, type[Number]] | None = None,
        manual: dict[str, Number] | None = None,
        daily: dict[str, Number] | None = None,
        weekly: dict[str, Number] | None = None,
        monthly: dict[str, Number] | None = None,
        yearly: dict[str, Number] | None = None,
    ) -> None:
        if not isinstance(owner, ABFModel) and not isinstance(owner, ABFAgent):
            raise TypeError("Calendar 'owner' must be a valid model or agent object")

        self.model = owner if isinstance(owner, ABFModel) else owner.model
        self.agent = owner if isinstance(owner, ABFAgent) else None
        
        counter_types = counter_types if counter_types is not None else {}
        manual = manual if manual is not None else {}
        daily = daily if daily is not None else {}
        weekly = weekly if weekly is not None else {}
        monthly = monthly if monthly is not None else {}
        yearly = yearly if yearly is not None else {}
        
        self.validate_names(
            set(counter_types.keys()),
            set(manual.keys()),
            set(daily.keys()),
            set(weekly.keys()),
            set(monthly.keys()),
            set(yearly.keys()),
        )
        
        self._counter_types: dict[str, type[Number]] = counter_types
        self._manual_counters: dict[str, Number] = manual
        self._daily_counters: dict[str, Number] = daily
        self._weekly_counters: dict[str, Number] = weekly
        self._monthly_counters: dict[str, Number] = monthly
        self._yearly_counters: dict[str, Number] = yearly
    
    def __repr__(self) -> str:
        return (
            f"Counters(\n"
            f"  owner: {self.agent if self.agent else self.model},\n"
            f"  manual: {self._manual_counters},\n"
            f"  daily: {self._daily_counters},\n"
            f"  weekly: {self._weekly_counters},\n"
            f"  monthly: {self._monthly_counters},\n"
            f"  yearly: {self._yearly_counters}\n"
            f")"
        )    
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def all(self) -> set[str]:
        """Returns a set of all counter names."""
        return set(self._counter_types.keys())
    
    @property
    def manual(self) -> set[str]:
        """Returns a set of all manual counter names."""
        return self(self._manual_counters.keys())
    
    @property
    def daily(self) -> set[str]:
        """Returns a set of all daily counter names."""
        return set(self._daily_counters.keys())
    
    @property
    def weekly(self) -> set[str]:
        """Returns a set of all weekly counter names."""
        return set(self._weekly_counters.keys())
    
    @property
    def monthly(self) -> set[str]:
        """Returns a set of all monthly counter names."""
        return set(self._monthly_counters.keys())
    
    @property
    def yearly(self) -> set[str]:
        """Returns a set of all yearly counter names."""
        return set(self._yearly_counters.keys())
    
    
    ###########
    # Methods #
    ###########
    
    def validate(self) -> None:
        self.validate_counters(
            set(self._counter_types.keys()),
            set(self._manual_counters.keys()),
            set(self._daily_counters.keys()),
            set(self._weekly_counters.keys()),
            set(self._monthly_counters.keys()),
            set(self._yearly_counters.keys()),
        )
    
    def validate_counter(self, name: str, value: Number, counter_type: type[Number]):
        """Checks that the name is not already used and that the value and type are valid."""
        if name in self.all:
            raise ValueError(f"Counter '{name}' already exists.")
        if not isinstance(value, Number):
            raise ValueError(f"initial_value must be a number; got {value}.")
        if not issubclass(counter_type, Number):
            raise ValueError(f"counter_type must be a numeric type; got {counter_type}.")
    
    def add_manual(
        self,
        name: str,
        initial_value: Number = 0,
        counter_type: type[Number] = float
    ) -> None:
        """Adds a manual counter."""
        self.validate_counter(name, initial_value, counter_type)
        
        self._counter_types[name] = counter_type
        self._manual_counters[name] = counter_type(initial_value)
    
    def add_daily(
        self, 
        name: str, 
        initial_value: Number = 0,
        counter_type: type[Number] = float
    ) -> None:
        """Adds a daily counter."""
        self.validate_counter(name, initial_value, counter_type)
        
        self._counter_types[name] = counter_type
        self._daily_counters[name] = counter_type(initial_value)
    
    def add_weekly(
        self, 
        name: str, 
        initial_value: Number = 0,
        counter_type: type[Number] = float
    ) -> None:
        """Adds a weekly counter."""
        self.validate_counter(name, initial_value, counter_type)
        
        self._counter_types[name] = counter_type
        self._weekly_counters[name] = counter_type(initial_value)
    
    def add_monthly(
        self, 
        name: str, 
        initial_value: Number = 0,
        counter_type: type[Number] = float
    ) -> None:
        """Add a monthly counter to the agent."""
        self.validate_counter(name, initial_value, counter_type)
        
        self._counter_types[name] = counter_type
        self._monthly_counters[name] = counter_type(initial_value)
    
    def add_yearly(
        self, 
        name: str, 
        initial_value: Number = 0,
        counter_type: type[Number] = float
    ) -> None:
        """Add a yearly counter to the agent."""
        self.validate_counter(name, initial_value, counter_type)
        
        self._counter_types[name] = counter_type
        self._yearly_counters[name] = counter_type(initial_value)
    
    def reset(self, name: str, value: Number = 0) -> None:
        """Reset a counter to a given value (default 0), preserving its declared type."""
        if name not in self.all:
            raise ValueError(f"Counter '{name}' does not exist.")
        
        ct = self._counter_types[name]
        if name in self._manual_counters:
            self._manual_counters[name] = ct(value)
        elif name in self._daily_counters:
            self._daily_counters[name] = ct(value)
        elif name in self._weekly_counters:
            self._weekly_counters[name] = ct(value)
        elif name in self._monthly_counters:
            self._monthly_counters[name] = ct(value)
        elif name in self._yearly_counters:
            self._yearly_counters[name] = ct(value)
        else:
            raise ValueError(f"Counter '{name}' not found in any group.")
    
    def reset_daily(self) -> None:
        """Reset all daily counters."""
        for key in self._daily_counters:
            self._daily_counters[key] = self._counter_types[key](0)
    
    def reset_weekly(self) -> None:
        """Reset all weekly counters."""
        for key in self._weekly_counters:
            self._weekly_counters[key] = 0
    
    def reset_monthly(self) -> None:
        """Reset all monthly counters."""
        for key in self._monthly_counters:
            self._monthly_counters[key] = 0
    
    def reset_yearly(self) -> None:
        """Reset all yearly counters."""
        for key in self._yearly_counters:
            self._yearly_counters[key] = 0
    
    def increment(self, name: str, value: Number = 1) -> None:
        """Increment a counter."""
        if name not in self.all:
            raise ValueError(f"Counter '{name}' not found.")
        
        ct = self._counter_types[name]
        if name in self._manual_counters:
            self._manual_counters[name] = ct(self._manual_counters[name] + value)
        elif name in self._daily_counters:
            self._daily_counters[name] = ct(self._daily_counters[name] + value)
        elif name in self._weekly_counters:
            self._weekly_counters[name] = ct(self._weekly_counters[name] + value)
        elif name in self._monthly_counters:
            self._monthly_counters[name] = ct(self._monthly_counters[name] + value)
        elif name in self._yearly_counters:
            self._yearly_counters[name] = ct(self._yearly_counters[name] + value)
