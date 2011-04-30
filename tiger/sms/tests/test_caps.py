from mock import Mock

from tiger.accounts.models import Site
from tiger.sales.models import Plan, Account
from tiger.sales.exceptions import CapExceeded, SoftCapExceeded, HardCapExceeded
from tiger.sms.sender import Sender
from tiger.utils.test import TestCase
from should_dsl import should, should_not


class PlanCapTestCase(TestCase):
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]

    def set_plan(self, plan_name):
        self.site.plan = Plan.objects.get(name=plan_name)
        self.site.save()
        sender = Sender(self.site, 'test')
        sender.get_sms_response = Mock(return_value={})
        sender.record_sms = Mock(return_value={})
        self.sender = sender

    def test_sms_no_cap(self):
        self.set_plan('no caps')
        (self.sender.add_recipients, '+14134370011', '+14132757010') |should_not| throw(CapExceeded)

    def test_sms_soft_cap(self):
        self.set_plan('soft caps')
        (self.sender.add_recipients, '+14134370011', '+14132757010') |should| throw(SoftCapExceeded)

    def test_sms_hard_cap(self):
        self.set_plan('hard caps')
        (self.sender.add_recipients, '+14134370011', '+14132757010') |should| throw(HardCapExceeded)
