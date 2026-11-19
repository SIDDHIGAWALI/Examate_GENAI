import pytest
from app.cal import sum, sub, div

@pytest.mark.parametrize("a,b,expected",[
    (10,20,30),
    (20,20,40)
])
def test_sum_cal(a,b,expected):
    assert sum(a,b) == expected


@pytest.mark.parametrize("a,b,expected",[
    (10,20,-10),
    (20,20,0),
    (10,5,5)
])
def test_sub_cal(a,b,expected):
    assert sub(a,b)==expected
