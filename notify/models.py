from django.db import models

from tiger.accounts.models import Site


class Fax(models.Model):
    DIRECTION_INBOUND = 1
    DIRECTION_OUTBOUND = 2
    DIRECTION_CHOICES = (
        (DIRECTION_INBOUND, 'Inbound'),
        (DIRECTION_OUTBOUND, 'Outbound'),
    )
    site = models.ForeignKey(Site)
    timestamp = models.DateTimeField()
    page_count = models.IntegerField()
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.timestamp = datetime.now()
        super(Fax, self).save(*args, **kwargs)
