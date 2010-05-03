from django import forms


class CancellationForm(forms.Form):
    comments = forms.CharField(required=False, widget=forms.Textarea)
