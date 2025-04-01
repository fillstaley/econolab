"""Counters Module for EconoLab

This module defines the core classes for tracking numerical quantities
in EconoLab, including the Counter class (an incrementable record of a
single measure) and the CounterCollection class, which manages a
collection of Counter objects for an agent or model.

Key Features:
- Counter: Uses __slots__ to minimize memory usage; supports
  incrementing, resetting and type validation.
- CounterCollection: Provides dictionary-like access and batch counter
  creation via add_counters. It also implements the iterator protocol
  for convenience.

Usage examples and further details are documented within the classes.

"""


from collections.abc import Iterator
from numbers import Number
from typing import Protocol, runtime_checkable


@runtime_checkable
class ABFModel(Protocol):
    pass


@runtime_checkable
class ABFAgent(Protocol):
    model: ABFModel


class Counter:
    """
    An incrementable counter for tracking a single numerical quantity.

    A Counter encapsulates a named numeric value along with a designated
    numeric type. It supports operations such as incrementing and resetting,
    and it enforces that its value is always stored using the specified
    type. The counter may be either transient (ie. it can be reset, and
    periodically is) or persistent (ie. it cannot be reset).

    Attributes
    ----------
    name : str
        A unique identifier for this counter.
    value : Number
        The current numeric value of the counter.
    persistent : bool
        Flag indicating whether the counter is persistent (True) or
        transient (False). Transient counters are periodically reset.

    Methods
    -------
    reset(value: Number = 0)
        If transient, reset the counter to the given value (default is 0).
    increment(amount: Number = 1)
        Increase the counter by the specified amount (default is 1).

    Notes
    -----
    This class uses __slots__ to limit instance attributes (name, _value,
    _type, persistent) and thus reduce memory overhead. The __repr__ and
    __str__ methods provide an unambiguous and human-readable representation
    of the counter, respectively.
    
    """

    __slots__ = ["name", "_value", "_type", "persistent"]
    
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def validate(value: Number, type_: type[Number]) -> None:
        if not isinstance(value, Number):
            raise ValueError(
                f"'value' must be a number; got {type(value)} instead."
            )
        if not issubclass(type_, Number):
            raise ValueError(
                f"'type_' must be a numeric type; got {type(type_)} instead."
            )
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(
        self, 
        name: str,
        init_value: Number = 0,
        type_: type[Number] = float,
        persistent: bool = False
    ) -> None:
        self.validate(init_value, type_)
        
        self.name: str = name
        self._value: Number = type_(init_value)
        self._type: type[Number] = type_
        self.persistent = persistent
    
    def __repr__(self) -> str:
        return f"Counter(name={self.name}, value={self.value}, type_={self._type})"
    
    def __str__(self) -> str:
        return f"'{self.name}' = {self.value}"
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def value(self) -> Number:
        """Returns the value of the counter."""
        return self._value
    
    @property
    def transient(self) -> bool:
        """Returns whether the counter can be reset or not."""
        return not self.persistent
    
    
    ###########
    # Methods #
    ###########
    
    def reset(self, value: Number = 0):
        """Sets the counter (if it is not persistent), defaults to 0."""
        if not self.persistent:
            self.validate(value, self._type)
            self._value = self._type(value)
    
    def increment(self, amount: Number = 1) -> None:
        """Increases the counter by an amount, defaults to 1."""
        self.validate(amount, self._type)
        self._value = self._type(self.value + amount)


class CounterCollection:
    """
    A collection for managing multiple Counter objects.
    
    CounterCollection provides a dictionary-like interface for accessing
    Counter objects which can be added with the add_counters() method.
    
    Attributes
    ----------
    model : ABFModel
        The model associated with this counter collection.
    agent : ABFAgent or None
        The agent associated with this counter collection (if applicable).

    Methods
    -------
    add_counters(type_: type[Number] = float, persistent: bool = False,
                 *null_counters: str, **init_counters: Number) -> None
        Add one or more counters to the collection. Positional arguments
        specify counter names with an initial value of 0, while keyword
        arguments specify counters with explicit initial values. All
        counters in the call share the same numeric type and persistence
        setting.
    
    Additional Properties
    ---------------------
    all : dict[str, Counter]
        A dictionary view of all counters.
    transient : dict[str, Counter]
        A dictionary view of all transient (resettable) counters.
    persistent : dict[str, Counter]
        A dictionary view of all persistent counters.

    Notes
    -----
    Direct assignment and deletion (via __setitem__ and __delitem__) are
    disabled in order to ensure that counter values can only be modified
    via the provided methods (such as increment() and reset()), preserving
    the integrity of the counter collection during a model run.
    
    """
    
    
    ###################
    # Special Methods #
    ###################
    
    def __getitem__(self, name: str) -> Number:
        if name not in self._counters:
            raise ValueError(f"Counter '{name}' not found.")
        else:
            return self._counters[name].value
    
    def __setitem__(self, key, value):
        raise NotImplementedError(
            "Direct assignment is not allowed; use increment() or reset() instead."
        )

    def __delitem__(self, key):
        raise NotImplementedError("Deletion is not allowed.")
    
    def __iter__(self) -> Iterator[str]:
        return iter(self._counters)
    
    def __len__(self) -> int:
        return len(self._counters)
    
    def __contains__(self, key: str) -> bool:
        return key in self._counters
    
    def __init__(
        self,
        owner: ABFModel | ABFAgent,
        counters: dict[str, Counter] | None = None
    ) -> None:
        if not isinstance(owner, ABFModel) and not isinstance(owner, ABFAgent):
            raise TypeError(
                "CounterCollection 'owner' must be a valid model or agent object"
            )
        self.model = owner if isinstance(owner, ABFModel) else owner.model
        self.agent = owner if isinstance(owner, ABFAgent) else None
        
        self._counters: dict[str, Counter] = counters or {}
    
    def __repr__(self) -> str:
        return f"CounterCollection(owner={self.agent or self.model}, counters={self._counters})"
    
    
    ##############
    # Properties #
    ##############
    
    @property
    def all(self) -> dict[str, Counter]:
        """Returns the dictionary of counters."""
        return self._counters
    
    @property
    def transient(self) -> set[str]:
        """Returns a dictionary of transient counters."""
        return {
            name: counter
            for name, counter in self._counters.items() if counter.transient
        }
    
    @property
    def persistent(self) -> set[str]:
        """Returns a dictionary of persistent counters."""
        return {
            name: counter
            for name, counter in self._counters.items() if counter.persistent
        }
    
    
    ###########
    # Methods #
    ###########
    
    def add_counters(
        self,
        type_: type[Number] = float,
        persistent: bool = False,
        *null_counters: str,
        **init_counters: Number
    ) -> None:
        """
        Add one or more counters to the collection.

        This method registers new counters in the collection. They can
        be supplied in two ways:
        
        - As positional arguments, with each argument a string that
          names a counter with initial value 0.
        - As keyword arguments, with each keyword and value the name of
          a counter and its corresponding initial value.

        All counters added in this call will have the same numeric type
        (specified by 'type_') and the same persistence flag (specified
        by 'persistent'). If a counter with the same name already
        exists, a ValueError is raised.

        Parameters
        ----------
        type_ : type, optional
            The numeric type for the counters (default: float).
        persistent : bool, optional
            If True, the counters cannot be reset (default: False).
        *null_counters : str
            Counter names that will be initialized with a value of 0.
        **init_counters : Number
            Counter names and their corresponding initial values.

        Examples
        --------
        >>> counters = CounterCollection(agent)
        >>> counters.add_counters(type_=float, "revenue", expense=50.0)
        
        In this example, the 'revenue' counter is added with an initial
        value of 0.0 and the "expense" counter is added with an initial
        value of 50.0. Both are stored as floats and are not persistent.
        
        """
        
        counters = {name: 0 for name in null_counters} | init_counters
        for name, init_value in counters.items():
            if name in self._counters:
                raise ValueError(f"Counter '{name}' already exists.")
            self._counters[name] = Counter(name, init_value, type_, persistent)
