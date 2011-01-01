from tiger.stork import Stork, StorkConfigurationError
from tiger.stork.component import BaseComponent
from tiger.stork.font import FontComponent
from tiger.stork.swatch import SwatchComponent
from nose.tools import raises


def test_component_groups_contain_components():
    panels = Stork('stork/tests/fixtures/valid.yml')
    for panel in panels:
        for group in panel:
            for component in group:
                assert isinstance(component, BaseComponent)


def test_components_have_unique_keys():
    panels = Stork('stork/tests/fixtures/valid.yml')
    for panel in panels:
        for group in panel:
            for component in group:
                assert component.key == '%s-%s' % (panel.name.lower(), component.name.lower())


@raises(StorkConfigurationError)
def test_no_component_type_fails():
    panels = Stork('stork/tests/fixtures/no_component_type.yml')


@raises(StorkConfigurationError)
def test_invalid_component_type_fails():
    panels = Stork('stork/tests/fixtures/invalid_component_type.yml')


def test_all_components_are_in_cache():
    panels = Stork('stork/tests/fixtures/valid.yml')
    for panel in panels:
        for group in panel:
            for component in group:
                assert component in [v for k, v in panels.component_cache]
                assert panels[component.key] == component


def test_correct_subclass_is_assigned():
    panels = Stork('stork/tests/fixtures/valid.yml')
    assert isinstance(panels['foo-baz'], SwatchComponent)
    assert isinstance(panels['bar-quux'], FontComponent)
