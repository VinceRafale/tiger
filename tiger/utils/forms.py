from django import forms
from django.forms.util import ErrorList
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


class SpanErrorList(ErrorList):
    def __unicode__(self):
        return self.as_spans()

    def as_spans(self):
        if not self:
            return u''
        return mark_safe(''.join(
            u'<span class="errorlist">%s</span>' % conditional_escape(force_unicode(e)) for e in self
        ))


class BetterModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BetterModelForm, self).__init__(error_class=SpanErrorList, *args, **kwargs)
