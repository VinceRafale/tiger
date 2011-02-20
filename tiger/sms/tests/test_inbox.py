from datetime import timedelta
import faker
from tiger.accounts.models import Site
from tiger.sms.models import SMS
from tiger.utils.test import TestCase
from should_dsl import should, should_not


class SMSInboxTestCase(TestCase):
    poseur_fixtures = 'tiger.fixtures'
    
    def setUp(self):
        self.site = Site.objects.all()[0]
        self.numbers = [faker.phone_number.phone_number()[:20] for i in range(3)]
        for n in self.numbers:
            SMS.objects.create(
                settings=self.site.sms,
                body=faker.lorem.sentence(),
                conversation=True,
                phone_number=n,
                destination='inbound'
            )

    def test_message_count_updated(self):
        for n in self.numbers:
            SMS.objects.create(
                settings=self.site.sms,
                body=faker.lorem.sentence(),
                conversation=True,
                phone_number=n,
                destination='inbound'
            )
        first_thread = SMS.objects.inbox_for(self.site.sms)[0]
        first_thread.message_count |should| equal_to(2)

    def test_subscribe_smses_not_in_inbox(self):
        sms = SMS.objects.create(
            settings=self.site.sms,
            body='in',
            conversation=False,
            phone_number=self.numbers[0],
            destination='inbound'
        )
        sms |should_not| be_into(SMS.objects.inbox_for(self.site.sms))

    def test_older_sms_in_thread_not_in_inbox(self):
        sms = SMS.objects.create(
            settings=self.site.sms,
            body=faker.lorem.sentence(),
            conversation=True,
            phone_number=self.numbers[0],
            destination='inbound'
        )
        sms.timestamp -= timedelta(days=2)
        sms.save()
        sms |should_not| be_into(SMS.objects.inbox_for(self.site.sms))

    def test_reply_to_does_not_promote_inbox_position(self):
        numbers = [sms.phone_number for sms in SMS.objects.inbox_for(self.site.sms)]
        SMS.objects.create(
            settings=self.site.sms,
            body=faker.lorem.sentence(),
            conversation=True,
            phone_number=self.numbers[1],
            destination='outbound'
        ) 
        new_numbers = [sms.phone_number for sms in SMS.objects.inbox_for(self.site.sms)]
        numbers |should| equal_to(new_numbers)

    def test_reply_from_promotes_inbox_position(self):
        numbers = [sms.phone_number for sms in SMS.objects.inbox_for(self.site.sms)]
        SMS.objects.create(
            settings=self.site.sms,
            body=faker.lorem.sentence(),
            conversation=True,
            phone_number=self.numbers[1],
            destination='inbound'
        ) 
        new_numbers = [sms.phone_number for sms in SMS.objects.inbox_for(self.site.sms)]
        numbers |should_not| equal_to(new_numbers)
        numbers |should| include_all_of(new_numbers)
