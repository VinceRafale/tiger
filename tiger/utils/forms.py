from django import forms
from django.forms.models import BaseInlineFormSet
from django.forms.util import ErrorList
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

__all__ = ('RequireOneFormSet',)

class RequireOneFormSet(BaseInlineFormSet):
    """Require at least one form in the formset to be completed."""
    def clean(self):
        """Check that at least one form has been completed."""
        super(RequireOneFormSet, self).clean()
        for error in self.errors:
            if error:
                return
            completed = 0
        for cleaned_data in self.cleaned_data:
            # form has data and we aren't deleting it.
            if cleaned_data and not cleaned_data.get('DELETE', False):
                completed += 1
        if completed < 1:
            raise forms.ValidationError("At least one %s is required." %
                self.model._meta.object_name.lower())


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
