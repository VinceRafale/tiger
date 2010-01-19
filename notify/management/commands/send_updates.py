from datetime import datetime, timedelta

from django.core.mail import EmailMessage
from django.core.management.base import NoArgCommand

from tiger.accounts.models import Subscriber, ScheduledUpdate
from tiger.notify.tasks import SendEmailTask, SendFaxTask

class Notify(NoArgCommand):
    def handle_noargs(self, **options):
        now = datetime.now()
        # strip seconds and microseconds
        now = now - timedelta(seconds=now.second, microseconds=now.microsecond)
        t = now.time()
        dow = now.isoweekday()
        updates = ScheduledUpdate.objects.filter(start_time=t, weekday=dow)
        msgs = []
        for update in updates:
            site = update.site
            content = render_to_string('notify/update.html', {
                'specials': site.item_set.filter(special=True),
                'site': site
            })
            via_email = Subscriber.objects.via_email().filter(site=site)
            emails = [s.user.email for s in via_email]
            msg = EmailMessage('Latest specials from %s' % site.title, 
                content, bcc=emails)
            msgs.append(msg)
            via_fax = Subscriber.objects.via_fax().filter(site=site)
            SendFaxTask.delay(site=site, subscribers=via_fax, content=content)
        SendEmailTask.delay(msgs=msgs)



            

