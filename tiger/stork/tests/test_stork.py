from tiger.accounts.models import Site
from tiger.stork import Stork, StorkConfigurationError

import cssutils
from lxml.html import fromstring

from poseur.fixtures import load_fixtures

from nose.tools import *
from django import forms
from django.core.management import call_command
from django.utils import simplejson as json


def run_fixtures():
    if not Site.objects.count():
        load_fixtures('tiger.fixtures')
        call_command('loaddata', 'stork/fixtures/initial_data.json')


@with_setup(run_fixtures)
def test_outputs_swatch_json():
    panels = Stork('stork/tests/fixtures/valid.yml', site=Site.objects.all()[0])
    swatch_json_as_list = json.loads(panels.swatch_json())
    assert swatch_json_as_list == [
        s.for_json()
        for s in panels.swatches
    ]

@with_setup(run_fixtures)
def test_outputs_valid_css():
    panels = Stork('stork/tests/fixtures/valid.yml', site=Site.objects.all()[0])
    panels.save()
    css = panels.css()
    parsed = cssutils.parseString(css)
    rule_count = 0
    for component in panels.component_cache:
        if hasattr(component, 'properties'):
            rule_count += len(component.properties)
        else:
            rule_count += 1
    assert len(parsed.cssRules) == rule_count

@with_setup(run_fixtures)
def test_compresses_css():
    panels = Stork('stork/tests/fixtures/valid.yml', site=Site.objects.all()[0])
    panels.save()
    css = panels.css()
    compressed = panels.compressed_css()
    assert len(css) > len(compressed)
