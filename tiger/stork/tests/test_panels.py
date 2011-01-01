from tiger.stork import Stork, StorkConfigurationError
from tiger.stork.component import ComponentGroup

from nose.tools import raises


def test_create_panels():
    panels = Stork('stork/tests/fixtures/valid.yml')
    assert len(panels) == 2


@raises(StorkConfigurationError)
def test_duplicate_panel_names():
    Stork('stork/tests/fixtures/duplicate_panels.yml')
        

def test_panel_contents_are_component_groups():
    panels = Stork('stork/tests/fixtures/valid.yml')
    for panel in panels:
        for group in panel:
            assert isinstance(group, ComponentGroup)


def test_component_groups_link_back_to_panels():
    panels = Stork('stork/tests/fixtures/valid.yml')
    for panel in panels:
        for group in panel:
            assert group.panel == panel
