from datetime import time

from django import forms


class SelectableTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None, date_format=None, time_format=None):
        widgets = (forms.Select(choices=[(i, '%02d' % i) for i in range(1, 13)]),
                   forms.Select(choices=[(i, '%02d' % i) for i in range(0, 60, 5)]),
                   forms.Select(choices=(('am', 'am'), ('pm', 'pm'))))
        super(SelectableTimeWidget, self).__init__(widgets, {"class": "timeselector"})

    def decompress(self, value):
        if value:
            return [value.hour % 12 or 12, value.minute, "am" if value.hour < 12 else "pm"]
        return [None, None, None]


class SelectableTimeField(forms.MultiValueField):
    widget = SelectableTimeWidget
    
    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(),
            forms.IntegerField(),
            forms.CharField(),
        )
        super(SelectableTimeField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            hours, minutes, meridian = data_list
            if meridian.lower() == 'pm' and hours != 12:
                hours += 12  
            return time(hours, minutes)
        return None
