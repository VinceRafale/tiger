from poseur.fixtures import FakeModel, FakeField

from django.contrib.auth.models import User
from django.conf import settings

from tiger.accounts.models import Account, Site


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

    class Meta:
        model = Site
        count = 1
        requires = (FakeAccount, FakeUser,)


class FakePolygonField(FakeField):
    def get_random_value(self, lower=None, upper=None):
        return None
