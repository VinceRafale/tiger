from datetime import datetime, timedelta

from django.core import mail
from django.core.management.base import NoArgsCommand

from celery.task import Task, PeriodicTask
from celery.registry import tasks

from tiger.accounts.models import Subscriber, ScheduledUpdate
from tiger.notify.fax import FaxMachine, FaxServiceError
from tiger.utils.pdf import render_to_pdf



class SendFaxTask(Task):
    def run(self, site, subscribers, content, **kwargs):
        fax_machine = FaxMachine(site)
        try:
            return fax_machine.send(subscribers, content, **kwargs)
        except FaxServiceError, e:
            self.retry([site, subscribers, content], kwargs,
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
            content = render_to_pdf('notify/update.html', {
                'specials': site.item_set.filter(special=True).order_by('section__id'),
                'footer': update.footer,
                'site': site,
                'show_descriptions': update.show_descriptions
            })
            via_email = Subscriber.via_email.filter(site=site)
            emails = [s.user.email for s in via_email]
            msg = mail.EmailMessage('Latest specials from %s' % site.name, 
                content, bcc=emails)
            msgs.append(msg)
            via_fax = Subscriber.via_fax.filter(site=site)
            SendFaxTask.delay(site=site, subscribers=via_fax, content=content)
        SendEmailTask.delay(msgs=msgs)
    

tasks.register(RunScheduledBlastTask)
