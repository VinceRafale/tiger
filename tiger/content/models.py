from decimal import Decimal
import os.path

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.template.defaultfilters import slugify

from imagekit.models import ImageModel
from pyPdf import PdfFileReader

from tiger.utils.pdf import render_to_pdf


class Content(models.Model):
    TYPE_HOMEPAGE = 'homepage'
    TYPE_FINDUS = 'find-us'
    TYPE_ABOUT = 'about'
    CONTENT_TYPES = (
        TYPE_HOMEPAGE,
        TYPE_FINDUS,
        TYPE_ABOUT,
    )
    site = models.ForeignKey('accounts.Site')
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
    site = models.ForeignKey('accounts.Site')
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='uploaded_images')
    slug = models.SlugField(editable=False, default='')
    description = models.TextField(blank=True, default='')

    class IKOptions:
        spec_module = 'tiger.content.specs'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(ItemImage, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return 'image_detail', (), {'image_id': self.id, 'slug': self.slug}


class PdfMenu(models.Model):
    CONTENT_CHOICES = (
        ('S', 'Specials'), 
        ('A', 'All menu items')
    )
    site = models.ForeignKey('accounts.Site')
    name = models.CharField(max_length=100, help_text='This description is for your reference only.  It will not appear in your blasts.', default='')
    title = models.CharField(max_length=255, blank=True, help_text='The title as it will appear in the blast.', default='')
    columns = models.SmallIntegerField('number of columns', default=2)
    column_height = models.DecimalField('column height (in inches)', default='7.0', decimal_places=1, max_digits=3) 
    orientation = models.CharField(max_length=1, choices=(('P', 'Portrait'), ('L', 'Landscape')))
    footer = models.TextField(blank=True, help_text='This text will appear at the bottom of e-mails and faxes sent at this time.')
    content = models.CharField(max_length=1, choices=CONTENT_CHOICES)
    show_descriptions = models.BooleanField('check to include the descriptions of your menu items', default=True)
    featured = models.BooleanField(default=False)
    page_count = models.PositiveIntegerField(default=1)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            super(PdfMenu, self).save(*args, **kwargs)
        f = open(self.path, 'w')
        f.write(self.render())
        f.close()
        reader = PdfFileReader(open(self.path))
        self.page_count = reader.getNumPages()
        super(PdfMenu, self).save(*args, **kwargs)

    def render(self):
        columns = self._get_columns() 
        return render_to_pdf('notify/update.html', {
            'sections': self.site.section_set.all(),
            'title': self.title,
            'footer': self.footer,
            'site': self.site,
            'show_descriptions': self.show_descriptions,
            'columns': columns,
            'show_all': self.content == 'A',
            'landscape': True if self.orientation == 'L' else False
        })

    def _get_columns(self):
        columns = []
        height = self.column_height
        gutter = Decimal('0.125')
        margin = Decimal('0.6')
        page_width =  Decimal('9.8') if self.orientation == 'L' else Decimal('7.3')
        width = page_width / self.columns - gutter
        for i in range(self.columns):
            left = margin + gutter * i + (page_width / self.columns) * i
            columns.append(dict(height=height, width=width, left=left))
        return columns

    @property
    def _tail(self):
        return 'pdfmenus/%s-%d.pdf' % (slugify(self.name), self.id)

    @property
    def path(self):
        return os.path.join(settings.MEDIA_ROOT, self._tail)

    @property
    def url(self):
        return settings.MEDIA_URL + self._tail


admin.site.register(ItemImage)
