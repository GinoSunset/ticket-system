from django.forms.widgets import Input, Select, RadioSelect


class CalendarInput(Input):
    input_type = "text"
    template_name = "ticket/widgets/calendar.html"


class ContractorSelect(Select):
    template_name = "ticket/widgets/contractor_input.html"


class FomanticRadioSelect(RadioSelect):
    template_name = "ticket/widgets/fomantic_radio.html"
