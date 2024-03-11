from django.forms import Select


class Dropdown(Select):
    template_name = "ticsys/widgets/dropdown.html"
