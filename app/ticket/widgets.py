from django.forms.widgets import Input, Select


class CalendarInput(Input):
    input_type = "text"
    template_name = "ticket/widgets/calendar.html"


class ContractorSelect(Select):
    template_name = "ticket/widgets/contractor_select.html"
    option_template_name = "ticket/widgets/contractor_option.html"

    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)
        if value:
            contractor = self.choices.queryset.get(pk=value.value)
            if hasattr(contractor, "profile_contractor"):
                option["city"] = contractor.profile_contractor.city
                option["region"] = contractor.profile_contractor.region
        return option


class PhoneInput(Input):
    template_name = "ticket/widgets/phone.html"


class PhoneInputWithoutAdd(Input):
    template_name = "ticket/widgets/phone_without_add.html"
