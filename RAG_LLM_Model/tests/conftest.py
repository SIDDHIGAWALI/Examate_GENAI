import pytest


@pytest.fixture
def sample_user():
    return {
        "id": 101,
        "name": "Rahul",
        "email": "rahul@gmail.com",
        "age": 25
    }