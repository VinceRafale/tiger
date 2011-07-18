from datetime import datetime, timedelta
from django.conf import settings
from pytz import timezone
from django.utils.safestring import mark_safe


DOW_MONDAY = 0
DOW_TUESDAY = 1
DOW_WEDNESDAY = 2
DOW_THURSDAY = 3
DOW_FRIDAY = 4
DOW_SATURDAY = 5
DOW_SUNDAY = 6
DOW_CHOICES = (
    (DOW_MONDAY, 'Monday'),
    (DOW_TUESDAY, 'Tuesday'),
    (DOW_WEDNESDAY, 'Wednesday'),
    (DOW_THURSDAY, 'Thursday'),
    (DOW_FRIDAY, 'Friday'),
    (DOW_SATURDAY, 'Saturday'),
    (DOW_SUNDAY, 'Sunday'),
)

TIME_OPEN = 'open'
TIME_EOD = 'eod'
TIME_CLOSED = 'closed'

def is_available(timeslots, location, now, buff=0):
    site_tz = timezone(location.timezone)
    timeslots = timeslots.filter(dow=now.weekday())
    if not timeslots.count():
        return TIME_CLOSED
    for timeslot in timeslots:
        availability = timeslot.get_availability(location, now, buff)
        if availability is not None:
            return availability
    return TIME_CLOSED

def calculate_hour_string(timeslots, for_mobile=False):
    # this implementation is a little naive, but let's just assume our customers
    # don't keep ridiculous hours
    if type(timeslots) != list:
        timeslots = timeslots.order_by('dow')
    times = {}
    for timeslot in timeslots:
        time_range = '%s-%s' % (timeslot.pretty_start, timeslot.pretty_stop)
        if times.has_key(time_range):
            times[time_range].append(timeslot.dow)
        else:
            times[time_range] = [timeslot.dow]
    time_dict = dict(DOW_CHOICES)
    time_strings = []
    abbr_length = 3
    time_list = times.items()
    time_list.sort(key=lambda obj: obj[1][0])
    tmpl = '<p><strong>%s</strong> %s</p>' if for_mobile else '%s %s'
    for k, v in time_list:
        # test if the dow ints are consecutive
        if v == range(v[0], v[-1] + 1) and len(v) > 1:
            days = '%s-%s' % (time_dict[v[0]][:abbr_length], time_dict[v[-1]][:abbr_length],)
        else:
            days = '%s' % '/'.join(time_dict[n][:abbr_length] for n in v)
        
        time_strings.append(tmpl % (days, k,))
    hours_string = ('' if for_mobile else ', ').join(time_strings)
    return mark_safe(hours_string)
