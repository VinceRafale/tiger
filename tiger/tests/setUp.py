from django.contrib.auth.models import User

from tiger.accounts.models import *
from tiger.core.models import *

from poseur.fixtures import load_fixtures

def setup():
    load_fixtures('test.tiger.fixtures')
