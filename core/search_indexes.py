from haystack.indexes import *
from haystack import site

from tiger.core.models import Item


class ItemIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    site = IntegerField(model_attr='site__id')
    vegetarian = BooleanField(model_attr='vegetarian')
    spicy = BooleanField(model_attr='spicy')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Item.objects.all()


site.register(Item, ItemIndex)

