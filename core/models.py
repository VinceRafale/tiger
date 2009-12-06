from django.contrib.auth.models import User
from django.db import models

from django_extensions.db.fields import AutoSlugField
from imagekit.models import ImageModel


class Section(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, editable=False)
    description = models.TextField()
    slug = AutoSlugField(populate_from='name')

    class Meta:
        verbose_name = 'menu section'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('menu_section', kwargs={'section': self.slug})


class Item(ImageModel):
    name = models.CharField(max_length=100)
    section = models.ForeignKey(Section)
    user = models.ForeignKey(User, editable=False)
    image = models.ForeignKey('ItemImage', blank=True, null=True)
    description = models.TextField()
    special = models.BooleanField()
    slug = AutoSlugField(populate_from='name')

    class Meta:
        verbose_name = 'menu item'

    class IKOptions:
        spec_module = 'core.specs'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('menu_item', kwargs={'section': self.section.slug, 'item': self.slug})


class ItemImage(ImageModel):
    user = models.ForeignKey(User, editable=False)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='menu_images')


class Variant(models.Model):
    item = models.ForeignKey(Item)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __unicode__(self):
        return '%s: %s' % (self.item.name, self.description)


class Upgrade(models.Model):
    item = models.ForeignKey(Item)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    substitute = models.BooleanField(help_text='if selected, the display text \
        for this item will say "Substitute" instead of "Add"')

    class Meta:
        verbose_name = 'upgrade/substitution'
        verbose_name_plural = 'upgrades/substitutions'

    def __unicode__(self):
        return '%s %s for $%f more' % (
            'Substitute' if self.substitute else 'Add', 
            self.name, self.price)


class Order(models.Model):
    user = models.ForeignKey(User, editable=False)
    timestamp = models.DateTimeField()
    trans_id = models.IntegerField()
    

class LineItem(models.Model):
    order = models.ForeignKey(Order)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
