from django.contrib.auth.mixins import UserPassesTestMixin
from users.models import User, Operator

from .models import Comment


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


class AccessOperatorMixin(UserPassesTestMixin):
    def test_func(self):
        user: User = self.request.user
        if user.is_staff:
            return True
        if user.is_operator:
            return True
        return False


class AccessAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        user: User = self.request.user
        if user.is_staff:
            return True
        object_ = self.get_object()
        author = getattr(object_, self.author_field, None)
        if author is None:
            return False
        return author == user
