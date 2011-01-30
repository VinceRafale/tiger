from nose.tools import *
from poseur.fixtures import load_fixtures
from tiger.accounts.models import Site
from tiger.sales.models import Plan
from django.test import TestCase
from django.test.client import Client
from tiger import reseller_settings

def setup_plan(plan_name):
    def _setup():
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        site = Site.objects.all()[0]
        site.plan = Plan.objects.get(name=plan_name)
        site.save()

@with_setup(setup_plan('no caps'))
def test_sms_no_cap():
    site = Site.objects.all()[0]
    #sms model instance does not raise overage error
    #campaign cannot be saved
    assert False

@with_setup(setup_plan('soft caps'))
def test_sms_soft_cap():
    site = Site.objects.all()[0]
    #sms model instance raises overage error
    #campaign can be saved
    assert False

@with_setup(setup_plan('hard caps'))
def test_sms_hard_cap():
    #sms model instance raises overage error
    #campaign cannot be saved
    assert False
