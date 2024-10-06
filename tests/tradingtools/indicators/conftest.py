import pytest


@pytest.fixture
def input_data():
    return [1, 2, 1, 2, 3, 1]


@pytest.fixture
def input_high():
    return [1.5, 2.5, 1.5, 2.5, 3.5, 1.5]


@pytest.fixture
def input_low():
    return [0.5, 1.5, 0.5, 1.5, 2.5, 0.5]
