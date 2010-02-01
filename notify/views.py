import datetime

from django.http import HttpResponse

from tiger.notify.models import Fax

def record_fax(request):
    transaction_id = request.POST.get('TransactionID')
    page_count = int(request.POST.get('PagesSent'))
    completion_time = request.POST.get('CompletionTime')
    destination = request.POST.get('DestinationFax')
    # convert odd date format of completion time to datetime object
    date_str, time_str = completion_time.split()
    date = datetime.date(*[int(s) for s in reversed(date_str.split('/'))])
    time = datetime.time(*[int(s) for s in time_str.split(':')])
    completion = datetime.datetime.combine(date, time)
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
            completion_time=completion, destination=destination)
        return HttpResponse('')
    fax.page_count = page_count
    fax.completion_time = completion
    fax.destination = destination
    fax.save()
    return HttpResponse('')
