from django.contrib import admin
from django.contrib.auth.models import User

from tiger.core import site
from tiger.accounts.forms import *
from tiger.accounts.models import *


class SubscriberModelAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return SubscriberForm
        user = obj.user
        for attr in ('first_name', 'last_name', 'email'):
            SubscriberForm.declared_fields[attr].initial = getattr(user, attr, '')

    def save_model(self, request, obj, form, change):
        if change:
            user = obj.user
        else:
            user = User()
        for attr in ('first_name', 'last_name', 'email'):
            setattr(user, attr, form.cleaned_data[attr])
        user.save()
        obj.user = user
        obj.site = request.site    
        obj.save()
            

admin.site.register(Account)
admin.site.register(NotificationSettings)
admin.site.register(Site)
site.register(Subscriber, SubscriberModelAdmin)
