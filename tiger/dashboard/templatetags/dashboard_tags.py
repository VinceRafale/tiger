from django import template

register = template.Library()


@register.filter
def out_of_stock_at(val, arg):
    """Returns whether item ``val`` is out of stock at location ``arg``.
    """
    return val.locationstockinfo_set.get(location=arg).out_of_stock
