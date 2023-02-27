from django.apps import apps


def create_act_for_ticket(ticket):
    model = apps.get_model("reports", "Act")
    act = model.objects.create(ticket=ticket)
    return act
