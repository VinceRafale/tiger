from django import forms


class HoursAndMinutesWidget(forms.MultiWidget):
    def __init__(self, attrs=None, date_format=None, time_format=None):
        widgets = (forms.TextInput(), forms.TextInput())
        super(HoursAndMinutesWidget, self).__init__(widgets, {"class": "hours-and-minutes"})

    def decompress(self, value):
        if value:
            return [value / 60, value % 60]
        return [None, None]

    def format_output(self, rendered_widgets):
        return '<span>:</span>'.join(rendered_widgets)


class HoursAndMinutesField(forms.MultiValueField):
    widget = HoursAndMinutesWidget
    
    def __init__(self, *args, **kwargs):
        fields = (
            forms.CharField(),
            forms.CharField(),
        )
        super(HoursAndMinutesField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            hours, minutes = data_list
            return hours * 60 + minutes
        return None

