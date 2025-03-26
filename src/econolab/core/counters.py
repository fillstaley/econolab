"""...
"""


from numbers import Number


class Counters:
    """A collection of counters for an agent.
    """
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def validate_counters(
        counter_types: dict[str, type[Number]] | None,
        daily: dict[str, Number] | None,
        weekly: dict[str, Number] | None,
        monthly: dict[str, Number] | None,
        yearly: dict[str, Number] | None,
    ) -> None:
        """Validate that counter keys are unique across groups and match counter_types."""
        # Collect keys from each group
        daily_keys = set(daily.keys()) if daily is not None else {}
        weekly_keys = set(weekly.keys()) if weekly is not None else {}
        monthly_keys = set(monthly.keys()) if monthly is not None else {}
        yearly_keys = set(yearly.keys()) if yearly is not None else {}
        
        # Check that there are no overlaps between any groups:
        groups = {
            "daily": daily_keys,
            "weekly": weekly_keys,
            "monthly": monthly_keys,
            "yearly": yearly_keys,
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
        all_keys = daily_keys | weekly_keys | monthly_keys | yearly_keys
        ct_keys = set(counter_types.keys()) if counter_types is not None else {}
        if all_keys != ct_keys:
            missing = ct_keys - all_keys
            extra = all_keys - ct_keys
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
        counter_types: dict[str, type[Number]] | None = None,
        daily: dict[str, Number] | None = None,
        weekly: dict[str, Number] | None = None,
        monthly: dict[str, Number] | None = None,
        yearly: dict[str, Number] | None = None,
    ) -> None:
        
        self.validate_counters(
            counter_types,
            daily,
            weekly,
            monthly,
            yearly,
        )
        
        self._counter_types: dict[str, type[Number]] = (
            counter_types if counter_types is not None else {}
        )
        self._daily_counters: dict[str, Number] = daily if daily is not None else {}
        self._weekly_counters: dict[str, Number] = weekly if weekly is not None else {}
        self._monthly_counters: dict[str, Number] = monthly if monthly is not None else {}
        self._yearly_counters: dict[str, Number] = yearly if yearly is not None else {}
    
    def __repr__(self) -> str:
        return (
            f"Counters(\n"
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
        return self.daily | self.weekly
    
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
            self._counter_types,
            self._daily_counters,
            self._weekly_counters,
            self._monthly_counters,
            self._yearly_counters
        )
    
    def reset_daily(self) -> None:
        """Reset all daily counters."""
        for key in self._daily_counters:
            self._daily_counters[key] = 0
    
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
    
    def add_monthly(
        self, 
        name: str, 
        initial_value: Number | None = None,
        counter_type: type[Number] = float
    ) -> None:
        """Add a monthly counter to the agent."""
        if not issubclass(counter_type, Number):
            raise ValueError(f"counter_type must be a number; got {counter_type}.")
        
        if initial_value is not None and not isinstance(initial_value, Number):
            raise ValueError(f"initial_value must be a number; got {initial_value}.")
        
        if name in self.all:
            raise ValueError(f"Counter '{name}' already exists.")
        self._counter_types[name] = counter_type
        self._monthly_counters[name] = (
            counter_type(initial_value) if initial_value is not None else counter_type(0)
        )
    
    def add_yearly(
        self, 
        name: str, 
        initial_value: Number | None = None,
        counter_type: type[Number] = float
    ) -> None:
        """Add a yearly counter to the agent."""
        if not issubclass(counter_type, Number):
            raise ValueError(f"counter_type must be a number; got {counter_type}.")
        
        if initial_value is not None and not isinstance(initial_value, Number):
            raise ValueError(f"initial_value must be a number; got {initial_value}.")
        
        if name in self.all:
            raise ValueError(f"Counter '{name}' already exists.")
        self._counter_types[name] = counter_type
        self._yearly_counters[name] = (
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
        elif name in self._monthly_counters:
            self._monthly_counters[name] = ct(self._monthly_counters[name] + value)
        elif name in self._yearly_counters:
            self._yearly_counters[name] = ct(self._yearly_counters[name] + value)
