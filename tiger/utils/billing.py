import calendar
from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta 

def prorate(signup_date, amount):
    today = date.today()
    if signup_date > today:
        return Decimal("0.00")
    if today.day != 1:
        today = (today + relativedelta(months=1)).replace(day=1)
    one_month_ago = today + relativedelta(months=-1)
    if one_month_ago > signup_date.replace(day=1):
        return amount
    weekday, days = calendar.monthrange(one_month_ago.year, one_month_ago.month)
    days_in_service = days - signup_date.day
    return (amount * Decimal(
        str((days_in_service / float(days))))
    ).quantize(Decimal("1.00"))

