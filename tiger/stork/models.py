import base64
import time
from datetime import datetime
from django.core.files.base import ContentFile
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from tiger.stork.font_choices import WebFonts


class Theme(models.Model):
    name = models.CharField(max_length=100)
    saved_at = models.DateTimeField(auto_now=True)
    bundled_css = models.FileField(upload_to='stork/css', null=True)
    private = models.BooleanField(default=True)
    screenshot = models.ImageField(upload_to='screenshots', null=True, blank=True, default='')
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True, default='')
    thumb = ImageSpecField([ResizeToFill(75, 75)], image_field='screenshot')
    small = ImageSpecField([ResizeToFill(100, 100)], image_field='screenshot')
    medium = ImageSpecField([ResizeToFill(240, 240)], image_field='screenshot')
    large = ImageSpecField([ResizeToFill(500, 500)], image_field='screenshot')

    def update(self, css):
        filename = '%d-%d.css' % (self.id, int(time.mktime(datetime.now().timetuple())))
        self.bundled_css.save(filename, ContentFile(css.encode('utf-8')))


class Component(models.Model):
    theme = models.ForeignKey(Theme)
    component = models.CharField(max_length=50)

    class Meta:
        abstract = True


class Swatch(Component):
    color = models.CharField(max_length=12)
    alpha = models.DecimalField(max_digits=2, decimal_places=1, default='1.0')


class FontStack(models.Model):
    name = models.CharField(max_length=20)
    ttf = models.FileField(upload_to='fonts/ttf', null=True)
    eot = models.FileField(upload_to='fonts/eot', null=True)
    woff = models.FileField(upload_to='fonts/woff', null=True)
    svg = models.FileField(upload_to='fonts/svg', null=True)
    stack = models.TextField(max_length=255, choices=WebFonts.FONT_CHOICES)
    data = models.TextField(default='')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.data and self.ttf:
            binary_data = self.ttf.read()
            b64_data = base64.encodestring(binary_data)
            self.data = b64_data.replace('\n', '').strip()
        super(FontStack, self).save(*args, **kwargs)


class Font(Component):
    font = models.ForeignKey(FontStack)


class Image(Component):
    image = models.ImageField('Background image (max. 1MB)', null=True, blank=True, upload_to='img/backgrounds')
    staged_image = models.ImageField('Background image (max. 1MB)', null=True, blank=True, upload_to='img/backgrounds')
    tiling = models.BooleanField('make this background image tile', default=False)


class Html(Component):
    invalid_html = models.TextField(null=True, blank=True)
    staged_html = models.TextField()
    html = models.TextField()


class CSS(Component):
    css = models.TextField()
