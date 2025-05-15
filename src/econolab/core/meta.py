"""A base metaclass for all EconoLab types.

This metaclass inherits from abc.ABCMeta. It also allows for class
attributes to be converted to constants, ie. read-only class and
instance properties.

"""

from __future__ import annotations

from abc import ABCMeta
from typing import Any, Callable, Self, Sequence


class EconoMeta(ABCMeta):
    """Metaclass for EconoLab types.
    
    This metaclass inherits from `abc.ABCMeta` and can be safely used with
    abstract base classes.
    
    This metaclass enforces immutability for class-level constants declared
    using the `class_constant` descriptor. Constants can be defined either
    by listing attribute names in the `__constant_attrs__` set within a
    class body, or by decorating methods with `@class_constant`. Attributes
    marked as constants cannot be reassigned or deleted after class creation,
    whether at the class or instance level. All constants, including those
    inherited from base classes, are collected in the `__constants__`
    attribute for introspection.
    """
    
    def __setattr__(cls, name: str, value: Any) -> None:
        if cls._is_class_constant(name, cls.__mro__):
            raise AttributeError(
                f"Cannot modify class constant '{cls.__name__}.{name}'."
            )
        super().__setattr__(name, value)
    
    def __delattr__(cls, name: str) -> None:
        if cls._is_class_constant(name, cls.__mro__):
            raise AttributeError(
                f"Cannot delete class constant '{cls.__name__}.{name}'."
            )
        return super().__delattr__(name)
    
    def __new__(
        meta, # type: ignore
        name: str,
        bases: tuple[type],
        namespace: dict,
        **kwargs
    ) -> EconoMeta:
        # extract user-specified constant attributes; make them class_constants
        constant_attrs = set(namespace.pop("__constant_attrs__", set()))
        for attr in constant_attrs:
            if isinstance(namespace.get(attr), class_constant):
                continue  # already handled via @-decorator
            value = namespace.pop(attr, None)
            namespace[attr] = meta._make_class_constant(value)
        
        cls = super().__new__(meta, name, bases, namespace)
        
        # add missing class_constants and those from parent classes
        for attr, val in cls.__dict__.items():
            if isinstance(val, class_constant):
                constant_attrs.add(attr)
        for base in cls.__mro__:
            constant_attrs.update(getattr(base, "__constants__", set()))
        
        cls.__constants__ = set(constant_attrs)
        return cls
    
    
    ##################
    # Static Methods #
    ##################
    
    @staticmethod
    def _is_class_constant(name: str, classes: Sequence[type]) -> bool:
        for cls in classes:
            attr = cls.__dict__.get(name, None)
            if isinstance(attr, class_constant):
                return True
        return False
    
    @staticmethod
    def _make_class_constant(value: Any) -> class_constant:
        return class_constant(lambda _: value)


class class_constant(property):
    """A read-only descriptor for defining class-level constants.

    Behaves like a class-level read-only property. It disallows assignment
    and deletion at both the instance and class levels. It also supports
    docstrings via the getter or explicit `doc` argument.
    """
    
    __slots__ = ("name",)
    
    
    ######################
    # Descriptor Methods #
    ######################
    
    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            instance = owner
        return super().__get__(instance, owner)
    
    def __set__(self, instance:  Any, value: Any) -> None:
        raise AttributeError(
            f"{self} of '{type(instance).__name__}' object cannot be modified."
        )
    
    def __delete__(self, instance: Any) -> None:
        raise AttributeError(
            f"{self} of '{type(instance).__name__}' object cannot be deleted."
        )
    
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
    
    
    ###################
    # Special Methods #
    ###################
    
    def __init__(self, fget: Callable[[Any], Any], doc: str | None = None) -> None:
        super().__init__(
            fget, fset=None, fdel=None, doc=doc or getattr(fget, "__doc__", None)
        )
    
    def __repr__(self) -> str:
        return f"class constant '{self.name}'"
