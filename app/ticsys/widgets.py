from django.forms import Select, CheckboxInput


class Dropdown(Select):
    template_name = "ticsys/widgets/dropdown.html"

MAKE THIS
class CheckboxUI(CheckboxInput):
    template_name = "ticsys/widgets/checkbox.html