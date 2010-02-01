# Create your views here.
from django.http import HttpResponse

from tiger.notify.models import Fax

def record_fax(request):
    transaction_id = request.POST.get('TransactionID')
    page_count = int(request.POST.get('PagesSent'))
    completion_time = request.POST.get('CompletionTime')
    destination = request.POST.get('DestinationFax')
    try:
        fax = Fax.objects.get(transaction=transaction_id)
    except Fax.DoesNotExist:
        parent_transaction_id = request.POST.get('ParentTransactionID')
        try:
            parent_fax = Fax.objects.get(transaction=parent_transaction_id)
        except Fax.DoesNotExist:
            return HttpResponse('')
        site = parent_fax.site
        Fax.objects.create(transaction=transaction_id, page_count=page_count, 
            parent_transaction=parent_transaction_id, site=site,
            completion_time=completion_time, destination=destination)
        return HttpResponse('')
    fax.page_count = page_count
    fax.completion_time = completion_time
    fax.destination = destination
    fax.save()
    return HttpResponse('')
