from django.db import models


class Component(models.Model):
    site = models.ForeignKey('accounts.Site')
    component = models.CharField(max_length=50)

    class Meta:
        abstract = True


class Swatch(Component):
    color = models.CharField(max_length=6)


class FontStack(models.Model):
    name = models.CharField(max_length=20)
    ttf = models.FileField(upload_to='fonts/ttf', null=True)
    eot = models.FileField(upload_to='fonts/eot', null=True)
    woff = models.FileField(upload_to='fonts/woff', null=True)
    svg = models.FileField(upload_to='fonts/svg', null=True)
    stack = models.TextField(max_length=255, choices=FONT_CHOICES)

    def __unicode__(self):
        return self.name


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
