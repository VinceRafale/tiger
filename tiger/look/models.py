import codecs
import os
import re
import time
from datetime import datetime

import cssmin

from imagekit.models import ImageModel

from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.db.models.signals import post_save
from django.template.loader import render_to_string

from tiger.look.constants import *

block_re = re.compile(r'\{% block ([a-z]+) %\}\s*\{% endblock %\}')

class FontFace(models.Model):
    name = models.CharField(max_length=20)
    ttf = models.FileField(upload_to='fonts/ttf')
    eot = models.FileField(upload_to='fonts/eot')
    woff = models.FileField(upload_to='fonts/woff')
    svg = models.FileField(upload_to='fonts/svg')
    stack = models.TextField(max_length=255, choices=FONT_CHOICES)

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
    name = models.CharField(max_length=20, blank=True)
    image = models.ImageField('Background image (max. 1MB)', null=True, blank=True, upload_to='img/backgrounds')
    staged_image = models.ImageField('Background image (max. 1MB)', null=True, blank=True, upload_to='img/backgrounds')
    color = models.CharField(max_length=6, default='D9D4D9', blank=True)
    repeat = models.CharField('tiling', max_length=9, default=REPEAT_BOTH, choices=REPEAT_CHOICES, blank=True)
    position = models.CharField(max_length=20, default='top left', choices=POSITION_CHOICES, blank=True)
    attachment = models.CharField('stickiness', max_length=7, choices=ATTACHMENT_CHOICES, default=ATTACHMENT_SCROLL, blank=True)

    def __unicode__(self):
        return self.name

    def as_css(self, staged=False):
       return render_to_string('look/background.css', {'bg': self, 'staged': staged}) 

    def clone(self, bg):
        self.image = bg.image
        self.color = bg.color
        self.repeat = bg.repeat
        self.position = bg.position
        self.attachment = bg.attachment
        self.save()


def get_default_font():
    try:
        return FontFace.objects.get(name='Chunk').id
    except:
        return 1


class Logo(ImageModel):
    image = models.ImageField('Choose your logo file', upload_to='img/logos', null=True, blank=True)

    class IKOptions:
        spec_module = 'tiger.look.specs'

    def as_css(self):
        return """#masthead h2 {
            background: url(%s) 0 center no-repeat;
            height: 102px;
            margin-top:0;
            margin-bottom:0;
            text-indent:-9999px;
        }
        """ % self.resized.url
    

class Skin(models.Model):
    site = models.OneToOneField('accounts.Site', null=True, editable=False)
    name = models.CharField(max_length=20)
    logo = models.ForeignKey(Logo, null=True, blank=True)
    staged_logo = models.ForeignKey(Logo, null=True, blank=True, verbose_name='Select your logo image file', related_name='temporary_skins')
    header_font = models.ForeignKey(FontFace, null=True, blank=True, default=get_default_font)
    body_font = models.TextField(max_length=255, choices=FONT_CHOICES, default=FONT_ARIAL)
    header_color = models.CharField(max_length=6, default='301613')
    body_color = models.CharField(max_length=6, default='000000')
    masthead_color = models.CharField(max_length=6, default='121012')
    masthead_font_color = models.CharField(max_length=6, default='E3E3BE')
    menu_color = models.CharField(max_length=6, default='2B292B')
    center_color = models.CharField(max_length=6, default='f5f5f5')
    button_color = models.CharField(max_length=6, default='C76218')
    button_text_color = models.CharField(max_length=6, default='f7f7f7')
    shaded_color = models.CharField('Accent color', max_length=6, default='bfccd1')
    background = models.ForeignKey(Background)
    css = models.TextField(blank=True, default=DEFAULT_CSS)
    pre_base = models.TextField(default=DEFAULT_PRE_BASE)
    staged_pre_base = models.TextField(default=DEFAULT_PRE_BASE)
    timestamp = models.DateTimeField(editable=False)

    def __unicode__(self):
        return self.name

    def save(self, bundle=True, *args, **kwargs):
        self.timestamp = datetime.now()
        if not self.name:
            self.name = self.site.name
        super(Skin, self).save(*args, **kwargs) 
        if bundle:
            f = codecs.open(self.path, 'w', 'utf-8')
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

    def custom_colors(self):
        return render_to_string('look/custom.css', {'skin': self})
        
    def bundle(self):
        uncompressed = render_to_string('look/template.css', {'skin': self})
        compressed = cssmin.cssmin(uncompressed)
        return compressed

    def clone(self, skin):
        self.header_font = skin.header_font
        self.body_font = skin.body_font
        self.header_color = skin.header_color
        self.body_color = skin.body_color
        self.masthead_color = skin.masthead_color
        self.masthead_font_color = skin.masthead_font_color
        self.menu_color = skin.menu_color
        self.center_color = skin.center_color
        self.button_color = skin.button_color
        self.button_text_color = skin.button_text_color
        self.shaded_color = skin.shaded_color
        self.background.clone(skin.background)
        self.css = skin.css
        self.save()

    def prepped_html(self):
        html = self.staged_pre_base
        for bit, tag in TEMPLATE_TAG_ESCAPES:
            html = html.replace(tag, bit)
        return block_re.sub(r'{{\1}}', html)


def new_site_setup(sender, instance, created, **kwargs):
    if created:
        Site = models.get_model('accounts', 'site')
        if isinstance(instance, Site):
            background = Background.objects.create(site=instance)
            skin = Skin.objects.create(site=instance, name=instance.name[:20], background=background)


admin.site.register(FontFace)
admin.site.register(Background)
admin.site.register(Skin)

post_save.connect(new_site_setup)
