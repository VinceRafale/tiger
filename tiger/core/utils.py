from tiger.utils.pdf import render_to_pdf
from tiger.notify.tasks import SendFaxTask

def notify_restaurant(order, status):
	content = render_to_pdf('notify/order.html', {'order': order, 'cart': order.cart, 'order_no': order.id})
	site = order.site
	SendFaxTask.delay(site, site.fax_number, content, IsFineRendering=True)
	order.status = status
	order.save()

