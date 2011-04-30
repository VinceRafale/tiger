from haystack.indexes import *
from haystack import site

from django.conf import settings

from tiger.core.models import Item


class ItemIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    site = IntegerField(model_attr='site__id')
    item = CharField(model_attr='name')
    section = CharField(model_attr='section__name')
    vegetarian = BooleanField(model_attr='vegetarian')
    spicy = BooleanField(model_attr='spicy')
    url = CharField(model_attr='get_absolute_url')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Item.objects.all()


if not settings.DEBUG:
    site.register(Item, ItemIndex)

