from poseur.fixtures import FakeModel, FakeField

from django.contrib.auth.models import User
from django.conf import settings

from tiger.accounts.models import Account, Site
from tiger.core.models import Item, Section, Variant, Order


class FakeUser(FakeModel):
    email = 'test@test.com'
    password = 'sha1$7e4e4$c4c5483c4cd38c9ae9674d9285308045ea900205' # "password"
    is_active = True

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
    custom_domain = False
    timezone = settings.TIME_ZONE
    managed = False
    enable_orders = True

    class Meta:
        model = Site
        count = 1
        requires = (FakeAccount, FakeUser,)


class FakePolygonField(FakeField):
    def get_random_value(self, lower=None, upper=None):
        return None


class FakeSection(FakeModel):
    name = ["Breakfast", "Sandwiches", "Dinners", "Salads"]
    ordering = None

    class Meta:
        model = Section
        count = 1
        requires = (FakeSite,)
    

class FakeItem(FakeModel):
    ordering = None
    price_list = None

    class Meta:
        model = Item
        count = 20
        requires = (FakeSection,)


class FakeVariant(FakeModel):
    price = ("3.00", "7.50",)

    class Meta:
        model = Variant
        count = 12
        requires = (FakeSection, FakeItem,)
    

class FakeOrder(FakeModel):
    timestamp = None

    class Meta:
        model = Order
        count = 0
