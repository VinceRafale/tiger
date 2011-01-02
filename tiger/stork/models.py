import time
from datetime import datetime
from django.core.files.base import ContentFile
from django.db import models

from tiger.stork.constants import FONT_CHOICES

from cumulus.storage import CloudFilesStorage

cloudfiles_storage = CloudFilesStorage()


class Theme(models.Model):
    name = models.CharField(max_length=100)
    saved_at = models.DateTimeField(auto_now=True)
    bundled_css = models.FileField(upload_to='stork/css', null=True, storage=cloudfiles_storage)
    private = models.BooleanField(default=True)

    def update(self, css):
        filename = '%d-%d.css' % (self.id, int(time.mktime(datetime.now().timetuple())))
        self.bundled_css.save(filename, ContentFile(css.encode('utf-8')))


class Component(models.Model):
    theme = models.ForeignKey(Theme)
    component = models.CharField(max_length=50)

    class Meta:
        abstract = True


class Swatch(Component):
    color = models.CharField(max_length=6)


class FontStack(models.Model):
    name = models.CharField(max_length=20)
    ttf = models.FileField(upload_to='fonts/ttf', null=True, storage=cloudfiles_storage)
    eot = models.FileField(upload_to='fonts/eot', null=True, storage=cloudfiles_storage)
    woff = models.FileField(upload_to='fonts/woff', null=True, storage=cloudfiles_storage)
    svg = models.FileField(upload_to='fonts/svg', null=True, storage=cloudfiles_storage)
    stack = models.TextField(max_length=255, choices=FONT_CHOICES)

    def __unicode__(self):
        return self.name


class Font(Component):
    font = models.ForeignKey(FontStack)


class Image(Component):
    image = models.ImageField('Background image (max. 1MB)', null=True, blank=True, upload_to='img/backgrounds', storage=cloudfiles_storage)
    staged_image = models.ImageField('Background image (max. 1MB)', null=True, blank=True, upload_to='img/backgrounds', storage=cloudfiles_storage)
    tiling = models.BooleanField('make this background image tile', default=False)


class Html(Component):
    invalid_html = models.TextField(null=True, blank=True)
    staged_html = models.TextField()
    html = models.TextField()


class CSS(Component):
    css = models.TextField()
