import faker
from poseur.fixtures import FakeModel

from django.contrib.auth.models import User

from tiger.accounts.models import *
from tiger.core.models import *


class FakeUser(FakeModel):
    email = 'test@test.com'
    password = 'sha1$7e4e4$c4c5483c4cd38c9ae9674d9285308045ea900205'

    class Meta:
        model = User
        count = 1


class FakeAccount(FakeModel):
    class Meta:
        model = Account
        count = 1
        requires = (FakeUser,)


class FakeSite(FakeModel):
    subdomain = 'foo'

    class Meta:
        model = Site
        count = 1
        requires = (FakeAccount, FakeUser,)


class FakeSection(FakeModel):
    name = ["Breakfast", "Sandwiches", "Dinners", "Salads"]
    ordering = None

    class Meta:
        model = Section
        count = 4
        requires = (FakeSite,)


class FakeVariant(FakeModel):
    price = ("3.00", "7.50",)

    class Meta:
        model = Variant
        count = 12
        requires = (FakeSection,)
    

class FakeItem(FakeModel):
    ordering = None
    price_list = None

    class Meta:
        model = Item
        count = 20
        requires = (FakeSection,)
    
