from datetime import datetime, timedelta

from tiger.accounts.models import Site
from tiger.notify.models import Release
from tiger.utils.test import TestCase


class ReleaseVisibilityTestCase(TestCase):
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]

    def test_visible_when_checked(self):
        """A release should be visible if it has been checked off as being
        published on the site.
        """
        release = Release.objects.create(
            site=self.site,
            title='foo',
            visible=True
        )
        assert release in list(Release.objects.visible())

    def test_not_visible_when_not_checked(self):
        """A release should not be visible if it is not checked off as being
        published on the site.
        """
        release = Release.objects.create(
            site=self.site,
            title='foo',
            visible=False
        )
        assert release not in list(Release.objects.visible())

    def test_visible_with_past_publish_date(self):
        """A release should be listed as visible if it has a publish date in
        the past.
        """
        release = Release.objects.create(
            site=self.site,
            title='foo',
            visible=True,
            publish_time=datetime.now() - timedelta(days=1)
        )
        assert release in list(Release.objects.visible())

    def test_not_visible_with_future_publish_date(self):
        """A release should not be visible if it has a publish date in the
        future.
        """
        release = Release.objects.create(
            site=self.site,
            title='foo',
            visible=True,
            publish_time=datetime.now() + timedelta(days=1)
        )
        assert release not in list(Release.objects.visible())
