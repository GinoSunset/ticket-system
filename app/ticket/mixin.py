from django.contrib.auth.mixins import UserPassesTestMixin
from users.models import User, Operator


class AccessTicketMixin(UserPassesTestMixin):
    def test_func(self):
        user: User = self.request.user
        ticket = self.get_object()
        if user.is_staff:
            return True
        if user.is_customer:
            return ticket.customer == user
        if user.is_contractor:
            return ticket.contractor == user
        if user.is_operator:
            operator: Operator = user.get_role_user()
            return ticket.customer in operator.get_customers()
        return ticket.creator == user
