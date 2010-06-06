import os
import time
from datetime import datetime

import cssmin

from django.conf import settings
from django.contrib import admin
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

    def as_css(self): 
        return render_to_string('look/font.css', {'hf': self}) 


class Background(models.Model):
    REPEAT_X = 'repeat-x'
    REPEAT_Y = 'repeat-y'
    REPEAT_BOTH = 'repeat'
    REPEAT_NONE = 'no-repeat'
    REPEAT_CHOICES = (
        (REPEAT_X, 'Across'),
        (REPEAT_Y, 'Up and down'),
        (REPEAT_BOTH, 'Both'),
        (REPEAT_NONE, 'None'),
    )
    ATTACHMENT_FIXED = 'fixed'
    ATTACHMENT_SCROLL = 'scroll'
    ATTACHMENT_CHOICES = (
        (ATTACHMENT_FIXED, 'Make background sticky'),
        (ATTACHMENT_SCROLL, 'Scroll background with page'),
    )
    POSITION_TOP_LEFT = 'left top'
    POSITION_TOP_CENTER = 'top'
    POSITION_TOP_RIGHT = 'right top'
    POSITION_MIDDLE_LEFT = 'left center'
    POSITION_MIDDLE_CENTER = 'center'
    POSITION_MIDDLE_RIGHT = 'right center'
    POSITION_BOTTOM_LEFT = 'left bottom'
    POSITION_BOTTOM_CENTER = 'center bottom'
    POSITION_BOTTOM_RIGHT = 'right bottom'
    POSITION_CHOICES = (
        (POSITION_TOP_LEFT, 'top left'),
        (POSITION_TOP_CENTER, 'top'),
        (POSITION_TOP_RIGHT, 'top right'),
        (POSITION_MIDDLE_LEFT, 'center left'),
        (POSITION_MIDDLE_CENTER, 'center'),
        (POSITION_MIDDLE_RIGHT, 'center right'),
        (POSITION_BOTTOM_LEFT, 'bottom left'),
        (POSITION_BOTTOM_CENTER, 'bottom center'),
        (POSITION_BOTTOM_RIGHT, 'bottom right'),
    )

    site = models.OneToOneField('accounts.Site', null=True, editable=False)
    name = models.CharField(max_length=20)
    image = models.ImageField(null=True, blank=True, upload_to='img/backgrounds')
    color = models.CharField(max_length=6, default='ffffff')
    repeat = models.CharField('tiling', max_length=9, default=REPEAT_BOTH, choices=REPEAT_CHOICES)
    position = models.CharField(max_length=20, default='top left', choices=POSITION_CHOICES)
    attachment = models.CharField('stickiness', max_length=7, choices=ATTACHMENT_CHOICES, default=ATTACHMENT_SCROLL)

    def __unicode__(self):
        return self.name

    def as_css(self):
       return render_to_string('look/background.css', {'bg': self}) 


class Skin(models.Model):
    site = models.OneToOneField('accounts.Site', null=True, editable=False)
    name = models.CharField(max_length=20)
    header_font = models.ForeignKey(FontFace, null=True, blank=True)
    header_color = models.CharField(max_length=6, default='000000')
    body_font = models.CharField(max_length=255, choices=FONT_CHOICES)
    header_color = models.CharField(max_length=6, default='000000')
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

    def clone(self, skin):
        self.header_font = skin.header_font
        self.body_font = skin.body_font
        self.background = skin.background
        self.css = skin.css
        self.save()


admin.site.register(FontFace)
admin.site.register(Background)
admin.site.register(Skin)
