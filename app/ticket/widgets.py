from django.forms.widgets import Input


class CalendarInput(Input):
    input_type = "text"
    template_name = "ticket/widgets/calendar.html"
