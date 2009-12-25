from celery.task import Task
from celery.registry import tasks

from tiger.notify.fax import FaxMachine

class SendFaxTask(Task):
    def run(self, site, contacts, content, **kwargs):
        fax_machine = FaxMachine(site)
        return fax_machine.send(contacts, content, **kwargs)


tasks.register(SendFaxTask)
