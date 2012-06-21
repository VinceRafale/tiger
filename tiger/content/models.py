from decimal import Decimal
import os.path

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from pyPdf import PdfFileReader

from tiger.utils.pdf import render_to_pdf

DEFAULT_CONTENT = 'Welcome to Takeout Tiger.  You can edit this content in your dashboard under Site > Content.'


class MenuItem(models.Model):
    MENU = 'menu'
    PAGE = 'page'
    UPLOAD = 'upload'
    URL = 'url'
    site = models.ForeignKey('accounts.Site')
    title = models.CharField(max_length=30)
    position = models.PositiveIntegerField(editable=False, null=True)
    url = models.URLField(null=True, blank=True)
    upload = models.FileField(upload_to='uploads', null=True, blank=True)
    page = models.ForeignKey('Content', null=True, blank=True)
    link_type = models.CharField(max_length=20)

    class Meta:
        ordering = ('position',)

    def save(self, *args, **kwargs):
        if not self.id:
            self.position = MenuItem.objects.filter(site=self.site).count() + 1
        super(MenuItem, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.position == 1:
            return '/'
        return {
            MenuItem.MENU: lambda: '/menu/',
            MenuItem.PAGE: lambda: self.page.get_absolute_url(),
            MenuItem.UPLOAD: lambda: self.upload.url,
            MenuItem.URL: lambda: self.url
        }[self.link_type]()

    def as_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'position': self.position,
            'linkType': self.link_type,
            'page': self.page_data,
            'url': self.url
        }

    @property
    def page_data(self):
        p = self.page
        if not p:
            return None
        return {
                'title': p.title,
                'text': p.text[:100] + '...',
                'url': p.get_absolute_url(),
                'edit_url': reverse('edit_page', args=[p.id])
        }



class Content(models.Model):
    TYPE_HOMEPAGE = 'homepage'
    TYPE_FINDUS = 'find-us'
    TYPE_ABOUT = 'about'
    CONTENT_TYPES = (
        TYPE_HOMEPAGE,
        TYPE_FINDUS,
        TYPE_ABOUT,
    )
    CONTENT_TYPE_TITLES = {
        TYPE_HOMEPAGE: 'Welcome!',
        TYPE_FINDUS: 'Find us',
        TYPE_ABOUT: 'About us',
    }
    LINK_TITLES = {
        TYPE_HOMEPAGE: 'Home',
        TYPE_FINDUS: 'Find us',
        TYPE_ABOUT: 'About',
    }
    site = models.ForeignKey('accounts.Site')
    slug = models.SlugField(editable=False)
    title = models.CharField(max_length=200, default='')
    text = models.TextField(default=DEFAULT_CONTENT)
    image = models.ForeignKey('ItemImage', null=True, blank=True)
    showcase = models.ForeignKey('ItemImage', null=True, blank=True, related_name='showcased_content_set')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Content, self).save(*args, **kwargs)
        cache.delete('%d-%s' % (self.site.id, self.slug))
        if MenuItem.objects.filter(page=self).count() == 0:
            MenuItem.objects.create(site=self.site, page=self, link_type=MenuItem.PAGE, title=Content.LINK_TITLES.get(self.slug, self.title))

    def is_default(self):
        return self.text == DEFAULT_CONTENT

    @models.permalink
    def get_absolute_url(self):
        return 'page_detail', [self.id, self.slug], {}
        


class ItemImage(models.Model):
    """Associates an image and its sizes with a user so that images 
    can easily be swapped out on menu items.
    """
    site = models.ForeignKey('accounts.Site')
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='uploaded_images')
    slug = models.SlugField(editable=False, default='')
    description = models.TextField(blank=True, default='')
    thumb = ImageSpecField([ResizeToFill(75, 75)], image_field='image')
    small = ImageSpecField([ResizeToFill(100, 100)], image_field='image')
    medium = ImageSpecField([ResizeToFill(240, 240)], image_field='image')
    large = ImageSpecField([ResizeToFill(500, 500)], image_field='image')

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(ItemImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for content in self.content_set.all():
            content.image = None
            content.save()
        for item in self.item_set.all():
            item.image = None
            item.save()
        super(ItemImage, self).delete(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return 'image_detail', (), {'image_id': self.id, 'slug': self.slug}


class PdfMenu(models.Model):
    site = models.ForeignKey('accounts.Site')
    name = models.CharField(max_length=100, help_text='This description is for your reference only.  It will not appear in your blasts.', default='')
    title = models.CharField(max_length=255, blank=True, help_text='The title as it will appear in the blast.', default='')
    columns = models.SmallIntegerField('number of columns', default=2)
    column_height = models.DecimalField('column height (in inches)', default='7.0', decimal_places=1, max_digits=3) 
    orientation = models.CharField(max_length=1, choices=(('P', 'Portrait'), ('L', 'Landscape')))
    footer = models.TextField(blank=True, help_text='This text will appear at the bottom of e-mails and faxes sent at this time.')
    show_descriptions = models.BooleanField('check to include the descriptions of your menu items', default=True)
    featured = models.BooleanField(default=False)
    sections = models.ManyToManyField('core.Section')
    page_count = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    def save(self, update=False, *args, **kwargs):
        super(PdfMenu, self).save(*args, **kwargs)
        if update:
            self.update()

    def update(self):
        f = open(self.path, 'w')
        f.write(self.render())
        f.close()
        reader = PdfFileReader(open(self.path))
        self.page_count = reader.getNumPages()
        self.save()
        

    def render(self):
        columns = self._get_columns() 
        return render_to_pdf('notify/update.html', {
            'sections': self.sections.all(),
            'title': self.title,
            'footer': self.footer,
            'site': self.site,
            'show_descriptions': self.show_descriptions,
            'columns': columns,
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


def new_site_setup(sender, instance, created, **kwargs):
    if created:
        Site = models.get_model('accounts', 'site')
        if isinstance(instance, Site):
            for content_type in Content.CONTENT_TYPES:
                Content.objects.create(site=instance, slug=content_type, title=Content.CONTENT_TYPE_TITLES[content_type])
            MenuItem.objects.create(site=instance, title='Menu', link_type=MenuItem.MENU)
            MenuItem.objects.create(site=instance, title='News', link_type=MenuItem.URL, url='/news/')


post_save.connect(new_site_setup)
