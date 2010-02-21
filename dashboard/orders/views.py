from django.views.generic.simple import direct_to_template

from tiger.core.models import Order

def home(request):
    return direct_to_template(request, template='dashboard/orders/home.html', extra_context={
        'orders': Order.objects.order_by('-timestamp')[:10] 
    })

def order_detail(request, order_id):
    return direct_to_template(request, template='dashboard/orders/order_detail.html', extra_context={
        'order': Order.objects.get(id=order_id) 
    })
