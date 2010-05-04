from django import forms
from django.contrib.auth import authenticate

class AuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, data=None, request=None, site=None, *args, **kwargs):
        self.request = request
        self.site = site
        super(AuthenticationForm, self).__init__(data, *args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password, site=self.site)
            if self.user_cache is None:
                raise forms.ValidationError("Please enter a correct username and password. Note that both fields are case-sensitive.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in.")

        return self.cleaned_data

    def get_user(self):
        return self.user_cache
