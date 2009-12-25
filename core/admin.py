from django.contrib import admin

from tiger.core import site
from tiger.core.models import *


class SectionModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user == obj.user

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user == obj.user


class VariantInline(admin.StackedInline):
    model = Variant


class UpgradeInline(admin.StackedInline):
    model = Upgrade


class ItemModelAdmin(admin.ModelAdmin):
    inlines = [VariantInline, UpgradeInline]
    
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user == obj.user

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user == obj.user


admin.site.register(Section)
admin.site.register(Item)
admin.site.register(Variant)
admin.site.register(Upgrade)
site.register(Item, ItemModelAdmin)
site.register(Section, SectionModelAdmin)
