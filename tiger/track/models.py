from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.utils import GeoIP


class Session(models.Model):
    site = models.ForeignKey('accounts.Site')
    session = models.CharField(max_length=32)
    is_closed = models.BooleanField(default=False)
    user_agent = models.TextField(default='')


class HitManager(models.Manager):
    def record_hit(self, site, location, session_id, response_code, request):
        """Records a single hit to the site, creating a session container where
        necessary and otherwise grabbing the appropriate session to add the hits
        to.

        New sessions should be created when:

        - there is no open session for the session_id/site/location combination
        - the referrer isn't from the site
        - it's been more than 10 minutes since the session was hit 
        """
        created = False
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        try:
            session = Session.objects.filter(
                site=site, session=session_id, is_closed=False, user_agent=user_agent
            ).order_by('-id')[0]
        except IndexError:
            session = Session.objects.create(site=site, session=session_id, user_agent=user_agent)
            created = True
        hit_number = 0
        session_is_stale = False
        if not created:
            # check how long it's been since the session was hit
            latest_hit = session.hit_set.order_by('-hit_number')[0]
            if datetime.now() - latest_hit.timestamp > timedelta(minutes=10):
                session_is_stale = True
            else:
                hit_number = latest_hit.hit_number + 1
        referrer = request.META.get('HTTP_REFERER', '')
        # if it's been a while since the last page hit, or if the session is open but
        # the referrer is from off-site, close the session and create a new one
        if session_is_stale or (not created and not referrer.startswith(unicode(site))):
            session.is_closed = True
            session.save()
            session = Session.objects.create(
                site=site, session=session_id, user_agent=user_agent)
        ip_address = request.META.get('HTTP_X_REAL_IP', request.META.get('REMOTE_ADDR'))
        hit = self.model.objects.create(
            location=location,
            session=session,
            path=request.path,
            referrer=referrer,
            verb=request.method,
            response_code=response_code,
            ip_address=ip_address,
            hit_number=hit_number
        )


class Hit(models.Model):
    session = models.ForeignKey(Session)
    location = models.ForeignKey('accounts.Location')
    path = models.CharField(max_length=255)
    referrer = models.TextField(blank=True)
    verb = models.CharField(max_length=6)
    response_code = models.PositiveIntegerField()
    timestamp = models.DateTimeField(default=datetime.now)
    ip_address = models.IPAddressField()
    coords = models.PointField(null=True)
    hit_number = models.PositiveIntegerField()
    objects = HitManager()

    def save(self, *args, **kwargs):
        g = GeoIP()
        self.coords = g.geos(self.ip_address)
        super(Hit, self).save(*args, **kwargs)
