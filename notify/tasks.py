from django.core import mail

from celery.task import Task
from celery.registry import tasks

from tiger.notify.fax import FaxMachine


class SendFaxTask(Task):
    def run(self, site, subscribers, content, **kwargs):
        fax_machine = FaxMachine(site)
        return fax_machine.send(subscribers, content, **kwargs)


class SendEmailTask(Task):
    def run(self, msgs, **kwargs):
        connection = mail.get_connection()
        connection.send_messages(msgs)


tasks.register(SendFaxTask)
tasks.register(SendEmailTask)
