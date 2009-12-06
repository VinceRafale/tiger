from haystack import indexes
from haystack import site

from tiger.core.models import Item


class ItemIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    section = indexes.CharField(model_attr='section')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Item.objects.all()


site.register(Item, ItemIndex)

