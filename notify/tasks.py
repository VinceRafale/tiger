import httplib
import urllib2
from datetime import datetime, timedelta

from django.core import mail
from django.core.management.base import NoArgsCommand
from django.db.models import get_model

from celery.task import Task, PeriodicTask
from celery.registry import tasks

from oauth import oauth

from tiger.accounts.models import Subscriber
from tiger.notify.fax import FaxMachine, FaxServiceError
from tiger.notify.utils import CONSUMER_KEY, CONSUMER_SECRET, SERVER, update_status
from tiger.utils.pdf import render_to_pdf

Social = get_model('notify', 'Social')


class SendFaxTask(Task):
    def run(self, site, recipients, content, **kwargs):
        fax_machine = FaxMachine(site)
        try:
            return fax_machine.send(recipients, content, **kwargs)
        except FaxServiceError, e:
            self.retry([site, recipients, content], kwargs,
                countdown=60 * 1, exc=e)


class SendEmailTask(Task):
    def run(self, msgs, **kwargs):
        connection = mail.get_connection()
        connection.send_messages(msgs)


class RunScheduledBlastTask(PeriodicTask):
    run_every = timedelta(minutes=1)

    def run(self, **kwargs):
        now = datetime.now()
        # strip seconds and microseconds
        now = now - timedelta(seconds=now.second, microseconds=now.microsecond)
        t = now.time()
        dow = now.isoweekday()
        updates = ScheduledUpdate.objects.filter(start_time=t, weekday=dow)
        msgs = []
        for update in updates:
            site = update.site
            columns = []
            for i in range(update.columns):
                height = update.column_height
                width = Decimal('7.3') / update.columns - Decimal('0.125')
                left = Decimal('0.6') + Decimal('0.125') * i + (Decimal('7.3') / update.columns) * i
                columns.append(dict(height=height, width=width, left=left))
            content = render_to_pdf('notify/update.html', {
                'specials': site.item_set.filter(special=True).order_by('section__id'),
                'title': update.title,
                'footer': update.footer,
                'site': request.site,
                'show_descriptions': update.show_descriptions,
                'columns': columns
            })
            via_email = Subscriber.via_email.filter(site=site)
            emails = [s.user.email for s in via_email]
            msg = mail.EmailMessage('Latest specials from %s' % site.name, 
                content, bcc=emails)
            msgs.append(msg)
            via_fax = Subscriber.via_fax.filter(site=site)
            numbers = [s.fax for s in via_fax]
            names = [contact.user.get_full_name() for contact in contacts]
            SendFaxTask.delay(site=site, recipients=numbers, content=content, names=names)
        SendEmailTask.delay(msgs=msgs)
    

class TweetNewItemTask(Task):
    def run(self, msg, token, secret, **kwargs):
        CONSUMER = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
        CONNECTION = httplib.HTTPSConnection(SERVER)
        access_token = oauth.OAuthToken(token, secret) 
        try:
            return update_status(CONSUMER, CONNECTION, access_token, msg)
        except urllib2.HTTPError:
            self.retry([msg, token, secret], kwargs,
                countdown=60 * 5, exc=e)


tasks.register(RunScheduledBlastTask)
