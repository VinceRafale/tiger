import twilio
from celery.task import Task

from tiger.sms.models import Campaign


class SmsBroadcastTask(Task):
    def run(self, campaign_id):
        campaign = Campaign.objects.get(id=campaign_id)
        campaign.broadcast()
