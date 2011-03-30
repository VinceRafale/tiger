import re

from component import BaseComponent
from errors import StorkConfigurationError

from lxml.html import fragments_fromstring, tostring
from lxml.html.clean import clean_html

from django import forms
from django.template.loader import render_to_string
from django.template import Template
from django.template.loader_tags import BlockNode
from django.utils.safestring import mark_safe

from tiger.stork.models import Html
from tiger.stork.constants import TEMPLATE_TAG_ESCAPES


block_re = re.compile(r'\{% block ([a-z]+) %\}\s*\{% endblock %\}')
pseudoblock_re = re.compile(r'\{\{([a-z]+)\}\}')


class HtmlComponent(BaseComponent):
    model = Html

    def __init__(self, panel, group, name, default=None, blocks=None, order=None, **kwargs):
        if default is None:
            raise StorkConfigurationError("A default value is required for html components")
        if blocks is None or len(blocks) < 1:
            raise StorkConfigurationError("A list of required blocks is required for html components")
        super(HtmlComponent, self).__init__(panel, group, name, order, **kwargs)
        self.default = default
        self.blocks = blocks

    def style_tag(self):
        return ''

    def get_css(self):
        return ''

    def get_defaults(self):
        return {
            'staged_html': self.prep_html(self.default),
        }

    def formfield_excludes(self):
        return ['html']

    def form_class(self):
        klass = super(HtmlComponent, self).form_class()
        blocks = self.blocks
        class HtmlForm(klass):
            def clean_staged_html(self):
                elements = fragments_fromstring(''.join([
                    c for c in self.cleaned_data['staged_html']
                    if c != '\r'
                ]))
                html = ''.join(tostring(clean_html(element)) for element in elements)
                with_blocks = pseudoblock_re.sub(r'&& block \1 &&&& endblock &&', html)
                for bit, tag in TEMPLATE_TAG_ESCAPES:
                    sub = ''.join(['&#%d;' % ord(c) for c in bit])
                    with_blocks = with_blocks.replace(bit, sub)    
                with_blocks = re.sub(r'&& block ([a-z]+) &&&& endblock &&', r'{% block \1 %}{% endblock %}', with_blocks)
                t = Template(with_blocks)
                required = list(blocks)
                invalid = []
                dups = []
                block_nodes = t.nodelist.get_nodes_by_type(BlockNode)
                for node in block_nodes:
                    name = node.name
                    if name in required:
                        required.remove(name)
                    else:
                        if name in blocks:
                            dups.append(name)
                        else:
                            invalid.append(name)
                if len(required):
                    raise forms.ValidationError(mark_safe("You are missing the following blocks: %s" % ', '.join('<code>{{%s}}</code>' % r for r in required)))
                if len(dups):
                    raise forms.ValidationError(mark_safe("The following blocks appear more than once: %s" % ', '.join('<code>{{%s}}</code>' % d for d in dups)))
                if len(invalid):
                    raise forms.ValidationError(mark_safe("The following blocks are invalid: %s" % ', '.join('<code>{{%s}}</code>' % i for i in invalid)))
                return with_blocks
        return HtmlForm

    def cleaned_form(self):
        form_class = self.form_class()
        instance = self.instance
        html = instance.invalid_html or instance.staged_html
        form = form_class({'%s-staged_html' % self.key: self.prep_html(html)}, instance=instance, prefix=self.key)
        form.full_clean()
        return form

    def save(self, data=None, files=None):
        new_instance = not self.instance
        if data is None:
            data = self.defaults
        form = self.form_instance(data, files)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.invalid_html = None
            if len(data) > 1 or new_instance:
                instance.html = instance.staged_html
        else:
            instance = self.instance
            instance.invalid_html = data['%s-staged_html' % self.key]
        instance.theme = self.stork.theme
        instance.component = self.key
        instance.save()

    def prep_html(self, html):
        for bit, tag in TEMPLATE_TAG_ESCAPES:
            html = html.replace(tag, bit)
        return block_re.sub(r'{{\1}}', html)

    def as_template(self, staged=False):
        if staged:
            field = 'staged_html'
        else:
            field = 'html'
        html = getattr(self.instance, field)
        pre_base_shell = """
            {%% extends 'head.html' %%}
            {%% block main %%}%s{%% endblock %%}""" % html
        return Template(pre_base_shell)

    def revert(self):
        instance = self.instance
        instance.staged_html = instance.html
        instance.invalid_html = None
        instance.save()
