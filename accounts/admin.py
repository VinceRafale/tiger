from django.contrib import admin

from tiger.core import site
from tiger.accounts.models import *


admin.site.register(Account)
admin.site.register(Site)
