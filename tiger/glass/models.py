from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify


class Post(models.Model):
    author = models.ForeignKey(User, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(editable=False)
    body = models.TextField()
    date_posted = models.DateField(default=date.today)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return 'post_detail', (), {'slug': self.slug, 'post_id': self.id}
