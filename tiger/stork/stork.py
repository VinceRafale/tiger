import cssmin
import yaml

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.utils.safestring import mark_safe

from errors import StorkConfigurationError
from panel import Panel
from font import FontComponent
from swatch import SwatchComponent
from record import Record

class Stork(object):
    """DOCS
    """
    def __init__(self, config_path, site=None):
        self.component_cache = []
        config = yaml.load(open(config_path).read())
        panel_names = [p['panel']['name'] for p in config]
        if len(panel_names) != len(set(panel_names)):
            raise StorkConfigurationError('Panel names must be unique')
        self.panels = [Panel(self, **p['panel']) for p in config]
        self.site = site

    def __len__(self):
        return len(self.panels)

    def __iter__(self):
        return iter(self.panels)

    def __getitem__(self, key):
        return dict(self.component_cache)[key]

    def _components_of_class(self, klass):
        return [
            v
            for k, v in self.component_cache
            if isinstance(v, klass)
        ]

    @property
    def swatches(self):
        return self._components_of_class(SwatchComponent)

    @property
    def fonts(self):
        return self._components_of_class(FontComponent)

    def save(self, data=None, files=None):
        for name, component in self.component_cache:
            component.save(data, files)

    def css(self):
        css_ordered_components = sorted([
            component for name, component in self.component_cache
        ], key=lambda x: x.order)
        return ''.join([
            c.get_css()
            for c in css_ordered_components
        ])

    def compressed_css(self):
        compressed = cssmin.cssmin(self.css())
        return compressed

    def swatch_json(self):
        return json.dumps([s.for_json() for s in self.swatches])

    def font_json(self):
        return json.dumps([f.for_json() for f in self.fonts])

    def toolbar(self):
        return render_to_string('stork/toolbar.html', {'panels': self, 'MEDIA_URL': settings.MEDIA_URL})

    def style_tags(self):
        return mark_safe(''.join(
            c.style_tag() 
            for c in sorted([
                component for name, component in self.component_cache
            ], key=lambda x: x.order)
        ))
