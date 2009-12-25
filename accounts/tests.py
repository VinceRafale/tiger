from django.test import TestCase

class NotificationSettingsTestCase(TestCase):
    def test_add_cron(self):
        """Tests that a new cron job is added to the crontab when
        notification settings are saved for the first time.
        """
        self.fail()

    def test_edit_cron(self):
        """Tests that an existing cron job is edited rather than
        created anew when notification settings are changed.
        """
        self.fail()

    def test_remove_cron(self):
        """Tests that a cron job is removed when notification
        settings are removed.
        """
        self.fail()

    def test_remove_cron_on_delete(self):
        """Tests that a notification settings object properly cleans
        up after itself when deleted.
        """
        self.fail()
