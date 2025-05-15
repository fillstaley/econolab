import pytest

from econolab.core import EconoMeta, class_constant


@pytest.fixture
def create_test_class():
    class SimpleClass(metaclass=EconoMeta):
        __constant_attrs__ = {"PI"}
        
        PI = 3.14159
        
        @class_constant
        def TAU(cls):
            return 6.28318
    return SimpleClass

@pytest.fixture
def create_test_instance(create_test_class):
    def _make_instance():
        return create_test_class()
    return _make_instance


def test_class_attribute_access(create_test_class):
    TestClass = create_test_class()
    assert TestClass.PI == 3.14159
    assert TestClass.TAU == 6.28318


def test_instance_attribute_access(create_test_instance):
    obj = create_test_instance()
    assert obj.PI == 3.14159
    assert obj.TAU == 6.28318


def test_class_attribute_assignment_raises(create_test_class):
    TestClass = create_test_class()
    with pytest.raises(AttributeError):
        TestClass.PI = 3

    with pytest.raises(AttributeError):
        TestClass.TAU = 3


def test_instance_attribute_assignment_raises(create_test_instance):
    obj = create_test_instance()
    with pytest.raises(AttributeError):
        obj.PI = 3

    with pytest.raises(AttributeError):
        obj.TAU = 3


def test_class_attribute_deletion_raises(create_test_class):
    TestClass = create_test_class()
    with pytest.raises(AttributeError):
        del TestClass.PI

    with pytest.raises(AttributeError):
        del TestClass.TAU


def test_instance_attribute_deletion_raises(create_test_instance):
    obj = create_test_instance()
    with pytest.raises(AttributeError):
        del obj.PI

    with pytest.raises(AttributeError):
        del obj.TAU


def test_constant_registry(create_test_class):
    TestClass = create_test_class()
    assert TestClass.__constants__ == {"PI", "TAU"}
