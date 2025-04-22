import pytest
from .utils.mock import TestModel, TestBorrower, TestLender

@pytest.fixture
def test_model():
    return TestModel()

@pytest.fixture
def test_borrower(test_model):
    return TestBorrower(test_model)

@pytest.fixture
def test_lender(test_model):
    return TestLender(test_model)
