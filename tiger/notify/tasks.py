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


class RunBlastTask(Task):
    def run(self, blast_id, **kwargs):
        Blast = get_model('notify', 'Blast')
        blast = Blast.objects.get(id=blast_id)
        site = blast.site
        content = open(blast.pdf.path).read()
        via_fax = blast.subscribers.filter(update_via=Subscriber.VIA_FAX)
        numbers = [s.fax for s in via_fax]
        names = [contact.user.get_full_name() for contact in via_fax]
        SendFaxTask.delay(site=site, recipients=numbers, content=content, names=names, PageOrientation=blast.pdf.get_orientation_display())
        # need HTML content or attachment....
        # via_email = Subscriber.via_email.filter(site=site)
        # emails = [s.user.email for s in via_email]
        # msg = mail.EmailMessage('Latest specials from %s' % site.name, 
        #     content, bcc=emails)
        # msgs.append(msg)
        # SendEmailTask.delay(msgs=msgs)
    

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
