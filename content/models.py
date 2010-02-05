from django.db import models

from imagekit.models import ImageModel

from tiger.accounts.models import Site


class Content(models.Model):
    TYPE_HOMEPAGE = 'homepage'
    TYPE_FINDUS = 'find-us'
    TYPE_ABOUT = 'about'
    CONTENT_TYPES = (
        TYPE_HOMEPAGE,
        TYPE_FINDUS,
        TYPE_ABOUT,
    )
    site = models.ForeignKey(Site)
    slug = models.SlugField(editable=False)
    title = models.CharField(max_length=200, default='')
    text = models.TextField(default='')
    image = models.ForeignKey('ItemImage', null=True)

    class Meta:
        unique_together = ('slug', 'site')


class ItemImage(ImageModel):
    """Associates an image and its sizes with a user so that images 
    can easily be swapped out on menu items.
    """
    site = models.ForeignKey(Site, editable=False)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='uploaded_images')

    class IKOptions:
        spec_module = 'tiger.content.specs'
