#import pytest
from app.user_services import *

def test_getusername(sample_user):
    assert get_user_name(sample_user) =="Rahul"

#pytest tests\test_user.py -v
