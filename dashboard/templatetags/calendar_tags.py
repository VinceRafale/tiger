from datetime import date, datetime, timedelta
from django import template

register = template.Library()

@register.inclusion_tag('dashboard/timeslot.json', takes_context=True)
def get_user_timeslots(context):
    """Generates a two-dimensional array of ``datetime`` objects and renders them
    as a JavaScript list of object literals.
    """
    site = context['site']
    timeslots = site.timeslot_set.all()
    weekday_for_today = date.today().weekday()
    schedule = [[]]
    # Sunday has to be special cased since jQuery plugin doesn't have option
    # of beginning on Monday
    sunday = date.today() + timedelta(days=(-1 - weekday_for_today))
    for slot in timeslots.filter(dow=6):
        schedule[0].append({
            "id": slot.id,
            "start": datetime.combine(sunday, slot.start),
            "end": datetime.combine(sunday, slot.stop)
        })
    for i in range(0, 6):
        weekday = date.today() + timedelta(days=(i - weekday_for_today))
        slots_for_weekday = []
        for slot in timeslots.filter(dow=i):
            cal_event = {
                "id": slot.id,
                "start": datetime.combine(weekday, slot.start),
                "end": datetime.combine(weekday, slot.stop)
            }
            slots_for_weekday.append(cal_event)
        schedule.append(slots_for_weekday)
    return {'schedule': schedule}
