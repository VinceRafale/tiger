import re
import importlib
from errors import StorkConfigurationError
from record import Record

from django import forms


non_alpha_re = re.compile(r'\W+')


def get_component(panel, group, data):
    try:
        component_type = data.pop('type')
    except KeyError:
        raise StorkConfigurationError('"type" declaration is required for components')
    try:
        mod = importlib.import_module('tiger.stork.%s' % component_type)
        klass = getattr(mod, '%sComponent' % component_type.title())
    except:
        raise StorkConfigurationError('"%s" is not a valid component type' % component_type)
    return klass(panel, group, **data)


class ComponentGroup(object):
    def __init__(self, panel, make_list=False, **data):
        self.panel = panel
        self.make_list = make_list
        self.components = [get_component(panel, self, c) for c in data['components']]

    def __iter__(self):
        return iter(self.components)


class BaseComponent(object):
    def __init__(self, panel, group, name, order, **kwargs):
        self.panel = panel
        self.stork = panel.stork
        self.group = group
        self.name = name
        self.order = order
        self.key = self._set_key()
        self.add_to_cache()

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.key)

    def _set_key(self):
        key_string = ('%s %s' % (self.panel.name, self.name)).lower()
        return non_alpha_re.sub('-', key_string)

    def add_to_cache(self):
        self.stork.component_cache.append((self.key, self))

    @property
    def style_tag_id(self):
        return 'st-st-%s' % self.key

    def style_tag(self):
        tag = self.get_style_tag()
        return tag % self.style_tag_contents()

    def get_style_tag(self):
        tag = '<style type="text/css" id="%s">%%s</style>' % self.style_tag_id
        return tag

    def style_tag_contents(self):
        """Retrieves the contents for this style tag based on the corresponding
        selection instance for ``site``.
        """
        return self.get_style_tag_contents()

    def get_style_tag_contents(self):
        raise NotImplementedError 

    def form_class(self):
        Model = self.model
        class ComponentForm(forms.ModelForm):
            class Meta:
                model = Model
                exclude = ['theme', 'component'] + self.formfield_excludes()
        overrides = self.get_formfield_overrides()
        if len(overrides):
            return type('CustomcomponentForm', (ComponentForm,), overrides)
        return ComponentForm

    def formfield_excludes(self):
        return []

    def form_instance(self, data=None, files=None):
        form_class = self.form_class()
        return form_class(data, files, instance=self.instance, prefix=self.key)

    @property
    def defaults(self):
        return dict([
            ('%s-%s' % (self.key, k), v)
            for k, v in self.get_defaults().items()
        ])
        
    def get_defaults(self):
        raise NotImplementedError

    def get_formfield_overrides(self):
        return {}

    def get_css(self):
        return self.get_style_tag_contents()

    def save(self, data=None, files=None):
        form_class = self.form_class()
        if data is None:
            data = self.defaults
        form = self.form_instance(data, files)
        form.full_clean()
        instance = form.save(commit=False)
        instance.theme = self.stork.theme
        instance.component = self.key
        instance.save()
        return instance

    @property
    def instance(self):
        try:
            return self.model.objects.get(
                theme=self.stork.theme,
                component=self.key
            )
        except self.model.DoesNotExist:
            return None
