from tiger.stork import Stork, StorkConfigurationError
from tiger.stork.swatch import SwatchComponent
from nose.tools import raises


@raises(StorkConfigurationError)
def test_swatch_requires_default():
    panels = Stork(config_path='stork/tests/fixtures/no_swatch_default.yml')


@raises(StorkConfigurationError)
def test_swatch_requires_properties():
    panels = Stork(config_path='stork/tests/fixtures/no_swatch_properties.yml')


def test_render_as_json():
    panels = Stork(config_path='stork/tests/fixtures/valid.yml')
    swatch = panels['foo-baz']
    swatch_as_array = [
       swatch.get_picker_id(),
       "#" + swatch.style_tag_id,
       swatch.get_hidden_input_id(),
       swatch.get_selector_prop()

    ]
    assert swatch_as_array == swatch.for_json()
