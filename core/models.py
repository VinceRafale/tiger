from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify

from imagekit.models import ImageModel

from tiger.accounts.models import Site


class Section(models.Model):
    """Acts as a container for menu items. Example: "Burritos".
    """
    name = models.CharField(max_length=50)
    site = models.ForeignKey(Site, editable=False)
    description = models.TextField()
    slug = models.SlugField(editable=False)

    class Meta:
        verbose_name = 'menu section'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Section, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu_section', kwargs={'section': self.slug})


class ItemManager(models.Manager):
    def render_specials_to_string(self, site, template='core/specials_fax.html'):
        items = self.filter(special=True, site=site)
        return render_to_string(template, {'site': site, 'items': items})


class Item(ImageModel):
    """Represents a single item on the menu in its most basic form.
    """
    name = models.CharField(max_length=100)
    section = models.ForeignKey(Section)
    site = models.ForeignKey(Site, editable=False)
    image = models.ForeignKey('ItemImage', blank=True, null=True)
    description = models.TextField()
    special = models.BooleanField()
    slug = models.SlugField(editable=False)
    objects = ItemManager()

    class Meta:
        verbose_name = 'menu item'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu_item', 
            kwargs={'section': self.section.slug, 'item': self.slug})


class ItemImage(ImageModel):
    """Associates an image and its sizes with a user so that images 
    can easily be swapped out on menu items.
    """
    site = models.ForeignKey(Site, editable=False)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='menu_images')

    class IKOptions:
        spec_module = 'core.specs'


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
        return '%s ($%s)' % (self.description, self.price)


class Upgrade(models.Model):
    """Provides additional cost data and/or order processing instructions. For
    example, "Subsitute seasoned frieds for $.50" or "Add extra cheese for
    $1.00." 
    """
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
