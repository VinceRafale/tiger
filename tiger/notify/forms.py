from datetime import datetime
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.utils.safestring import mark_safe

from tiger.core.fields import SelectableTimeField
from tiger.notify.models import Social, Release
from tiger.utils.forms import BetterModelForm
from tiger.utils.widgets import MarkItUpWidget


class TwitterForm(BetterModelForm):
    twitter_screen_name = forms.CharField(required=True)

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


class PublishForm(BetterModelForm):
    title = forms.CharField(widget=forms.Textarea, help_text="""
        This text will also be used as the content of Twitter and Facebook
        updates. For Twitter, it will be truncated if it (plus the link to your
        site that we insert) exceeds 140 characters.
    """)
    send_fax = forms.BooleanField(label='One of your fax lists', required=False)
    body = forms.CharField(widget=MarkItUpWidget, help_text=mark_safe("""

        This text will appear as the body for this publication on your website,
        your MailChimp campaign, and/or one page of the created fax.  Twitter
        and Facebook updates will link to it.<br />
        
        The plain text you type here gets converted to formatted HTML (preview
        on the right).  The plain text version will be used in e-mail campaigns
        for users who can't view HTML mail.

    """), required=False)
    when = forms.ChoiceField(widget=forms.RadioSelect, choices=(
        ('now', 'Publish immediately'),
        ('later', 'Schedule for the future'),
    ))
    publish_date = forms.DateField(widget=SelectDateWidget, required=False)
    publish_time = SelectableTimeField(required=False)

    class Meta:
        model = Release
        exclude = ('site', 'twitter', 'facebook', 'mailchimp', 'publish_time',)

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
        if mailchimp and not self.site.social.mailchimp_api_key:
            raise forms.ValidationError('You must connect a MailChimp account to post to MailChimp.')
        return mailchimp

    def clean_fax(self):
        fax = self.cleaned_data.get('fax')
        if fax and self.site.is_suspended:
            raise forms.ValidationError('Faxing charges are 10 cents per page delivered.  You do not have a valid credit card on file.  Please update your payment information.')
        return fax

    def clean_publish_time(self):
        publish_time = self.cleaned_data.get('publish_time')
        if publish_time:
            publish_date = self.cleaned_data.get('publish_date')
            publish_time = datetime.combine(publish_date, publish_time)
            if publish_time <= datetime.now():
                raise forms.ValidationError('Scheduled posts must be scheduled for the future.')
        return publish_time


class UpdatePublishForm(forms.ModelForm):
    title = forms.CharField(help_text='Warning: changing the title of an item you\'ve already published on your site can negatively impact the SEO benefits of the item.')
    class Meta:
        model = Release
        fields = ('title', 'body',)
