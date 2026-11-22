import pytest

from app import metrics


@pytest.fixture(autouse=True)
def clear_metrics():
    metrics.reset()
    yield