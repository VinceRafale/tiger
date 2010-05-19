from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.safestring import mark_safe

from tiger.accounts.models import Subscriber, FaxList
from tiger.notify.models import Social, Release
from tiger.utils.widgets import MarkItUpWidget


class TwitterForm(forms.ModelForm):
    class Meta:
        model = Social
        fields = ['twitter_screen_name']


class MailChimpForm(forms.ModelForm):
    mailchimp_send_blast = forms.ChoiceField(
        label='Would you like Takeout Tiger to create MailChimp campaigns to accompany your marketing blasts?',
        widget=forms.RadioSelect, choices=Social.CAMPAIGN_CHOICES)

    class Meta:
        model = Social
        fields = ['mailchimp_allow_signup', 'mailchimp_send_blast']


class PublishForm(forms.ModelForm):
    title = forms.CharField(widget=forms.Textarea, help_text="""
        This text will also be used as the content of Twitter and Facebook
        updates. For Twitter, it will be truncated if it (plus the link to your
        site that we insert) exceeds 140 characters.
    """)
    add_coupon = forms.BooleanField(label='Include a coupon?', required=False)
    add_pdf = forms.BooleanField(label='Include a menu as an attachment?', required=False)
    fax = forms.BooleanField(label='One of your fax lists', required=False)
    fax_list = forms.ModelChoiceField(queryset=FaxList.objects.all(), required=False)
    body = forms.CharField(widget=MarkItUpWidget, help_text=mark_safe("""

        This text will appear as the body for this publication on your website,
        your MailChimp campaign, and/or one page of the created fax.  Twitter
        and Facebook updates will link to it.<br />
        
        The plain text you type here gets converted to formatted HTML (preview
        on the right).  The plain text version will be used in e-mail campaigns
        for users who can't view HTML mail.

    """), required=False)
    twitter = forms.BooleanField(required=False)
    facebook = forms.BooleanField(required=False)
    mailchimp = forms.BooleanField(required=False)

    class Meta:
        model = Release
        exclude = ('site',)

    def __init__(self, data=None, files=None, site=None, *args, **kwargs):
        super(PublishForm, self).__init__(data=data, files=files, *args, **kwargs)
        self.fields['fax_list'].queryset = site.faxlist_set.all()
        self.site = site

    def clean_twitter(self):
        twitter = self.cleaned_data.get('twitter')
        if twitter and not self.site.twitter():
            raise forms.ValidationError('You must connect a Twitter account to post to Twitter.')
        return twitter

    def clean_facebook(self):
        facebook = self.cleaned_data.get('facebook')
        if facebook and not self.site.facebook():
            raise forms.ValidationError('You must connect a Facebook account to post to Facebook.')
        return facebook

    def clean_mailchimp(self):
        mailchimp = self.cleaned_data.get('mailchimp')
        if mailchimp and not self.site.mailchimp():
            raise forms.ValidationError('You must connect a MailChimp account to post to MailChimp.')
        return mailchimp
