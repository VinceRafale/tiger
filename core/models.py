from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.utils.http import int_to_base36
from django.utils.safestring import mark_safe

from imagekit.models import ImageModel

from tiger.accounts.models import Site
from tiger.notify.handlers import item_social_handler


class Section(models.Model):
    """Acts as a container for menu items. Example: "Burritos".
    """
    name = models.CharField(max_length=50)
    site = models.ForeignKey(Site, editable=False)
    description = models.TextField()
    slug = models.SlugField(editable=False)
    ordering = models.PositiveIntegerField(editable=False, default=1)

    class Meta:
        verbose_name = 'menu section'
        ordering = ('ordering',)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if not self.id:
            self.ordering = 1
        super(Section, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu_section', kwargs={'section': self.slug})


class ItemManager(models.Manager):
    def render_specials_to_string(self, site, template='core/specials_fax.html'):
        items = self.filter(special=True, site=site)
        return render_to_string(template, {'site': site, 'items': items})


class Item(models.Model):
    """Represents a single item on the menu in its most basic form.
    """
    name = models.CharField(max_length=100)
    section = models.ForeignKey(Section)
    site = models.ForeignKey(Site, editable=False)
    image = models.ForeignKey('content.ItemImage', blank=True, null=True)
    description = models.TextField(blank=True)
    special = models.BooleanField('is this menu item currently a special?')
    slug = models.SlugField(editable=False)
    ordering = models.PositiveIntegerField(editable=False, default=1)
    objects = ItemManager()

    class Meta:
        verbose_name = 'menu item'
        ordering = ('ordering',)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if not self.id:
            self.ordering = 1
        super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu_item', 
            kwargs={'section': self.section.slug, 'item': self.slug})

    def get_short_url(self):
        return reverse('short_code', kwargs={'item_id': int_to_base36(self.id)})


class Variant(models.Model):
    """Represents "column-level" extra data about a menu item.  This means
    information like "Extra large" and the corresponding price.  This is what a
    customer will actually be selecting when ordering a menu item.  All menu
    items must have at least one.  
    """
    item = models.ForeignKey(Item)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ['price']

    def __unicode__(self):
        s = '%s ($<span>%s</span>)' % (self.description, self.price)
        return mark_safe(s)


class Upgrade(models.Model):
    """Provides additional cost data and/or order processing instructions. For
    example, "Subsitute seasoned frieds for $.50" or "Add extra cheese for
    $1.00." 
    """
    item = models.ForeignKey(Item)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    substitute = models.BooleanField('Check here for the display text \
        for this item to say "Substitute" instead of "Add"')

    class Meta:
        verbose_name = 'upgrade/substitution'
        verbose_name_plural = 'upgrades/substitutions'

    def __unicode__(self):
        s = '%s %s for $<span>%.02f</span> more' % (
            'Substitute' if self.substitute else 'Add', 
            self.name, self.price)
        return mark_safe(s)


post_save.connect(item_social_handler, sender=Item)
