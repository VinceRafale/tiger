from datetime import datetime, timedelta

from django.core.management.base import NoArgsCommand

from tiger.notify.models import Release


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        now = datetime.now()
        stripped_now = now.replace(minute=0, second=0, microsecond=0)
        next_slot = stripped_now + timedelta(minutes=5)
        for r in Release.objects.filter(publish_time__gte=stripped_now).exclude(publish_time__gte=next_slot):
            r.send_all()
