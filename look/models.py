import os
import time
from datetime import datetime

import cssmin

from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string

FONT_ARIAL = 'Frutiger, "Frutiger Linotype", Univers, Calibri, "Gill Sans", "Gill Sans MT", "Myriad Pro", Myriad, "DejaVu Sans Condensed", "Liberation Sans", "Nimbus Sans L", Tahoma, Geneva, "Helvetica Neue", Helvetica, Arial, sans-serif'
FONT_GARAMOND = '"Palatino Linotype", Palatino, Palladio, "URW Palladio L", "Book Antiqua", Baskerville, "Bookman Old Style", "Bitstream Charter", "Nimbus Roman No9 L", Garamond, "Apple Garamond", "ITC Garamond Narrow", "New Century Schoolbook", "Century Schoolbook", "Century Schoolbook L", Georgia, serif'
FONT_GEORGIA = 'Constantia, "Lucida Bright", Lucidabright, "Lucida Serif", Lucida, "DejaVu Serif," "Bitstream Vera Serif", "Liberation Serif", Georgia, serif'
FONT_IMPACT = 'Impact, Haettenschweiler, "Franklin Gothic Bold", Charcoal, "Helvetica Inserat", "Bitstream Vera Sans Bold", "Arial Black", sans-serif'
FONT_MONOSPACE = 'Consolas, "Andale Mono WT", "Andale Mono", "Lucida Console", "Lucida Sans Typewriter", "DejaVu Sans Mono", "Bitstream Vera Sans Mono", "Liberation Mono", "Nimbus Mono L", Monaco, "Courier New", Courier, monospace'
FONT_TIMES = 'Cambria, "Hoefler Text", Utopia, "Liberation Serif", "Nimbus Roman No9 L Regular", Times, "Times New Roman", serif'
FONT_TREBUCHET = '"Segoe UI", Candara, "Bitstream Vera Sans", "DejaVu Sans", "Bitstream Vera Sans", "Trebuchet MS", Verdana, "Verdana Ref", sans-serif'
FONT_VERDANA = 'Corbel, "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", "DejaVu Sans", "Bitstream Vera Sans", "Liberation Sans", Verdana, "Verdana Ref", sans-serif'

FONT_CHOICES = (
    (FONT_ARIAL, 'Arial'),
    (FONT_GARAMOND, 'Garamond'),
    (FONT_GEORGIA, 'Georgia'),
    (FONT_IMPACT, 'Impact'),
    (FONT_MONOSPACE, 'Monospace'),
    (FONT_TIMES, 'Times New Roman'),
    (FONT_TREBUCHET, 'Trebuchet'),
    (FONT_VERDANA, 'Verdana'),
)

class FontFace(models.Model):
    name = models.CharField(max_length=20)
    ttf = models.FileField(upload_to='fonts')
    stack = models.CharField(max_length=255, choices=FONT_CHOICES)

    def __unicode__(self):
        return self.name


class Background(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(null=True, upload_to='img/backgrounds')
    color = models.CharField(max_length=6)
    repeat = models.CharField(max_length=8)
    position = models.CharField(max_length=20)
    attachment = models.CharField(max_length=7)

    def __unicode__(self):
        return self.name


class Skin(models.Model):
    name = models.CharField(max_length=20)
    header_font = models.ForeignKey(FontFace, null=True, blank=True)
    body_font = models.CharField(max_length=255, choices=FONT_CHOICES)
    background = models.ForeignKey(Background)
    css = models.TextField(blank=True)
    timestamp = models.DateTimeField(editable=False)
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.timestamp = datetime.now()
        super(Skin, self).save(*args, **kwargs) 
        f = open(self.path, 'w')
        f.write(self.bundle())

    @property
    def _tail(self):
        return 'skins/%d-%d.css' % (self.id, int(time.mktime(self.timestamp.timetuple())))

    @property
    def path(self):
        return os.path.join(settings.MEDIA_ROOT, self._tail)

    @property
    def url(self):
        return settings.MEDIA_URL + self._tail

    def bundle(self):
        uncompressed = render_to_string('look/template.css', {'skin': self})
        compressed = cssmin.cssmin(uncompressed)
        return compressed


admin.site.register(FontFace)
admin.site.register(Background)
admin.site.register(Skin)
