from django.contrib.auth.mixins import UserPassesTestMixin
from users.models import User, Operator


class AccessTicketMixin(UserPassesTestMixin):
    def test_func(self):
        user: User = self.request.user
        ticket = self.get_object()
        if user.is_anonymous:
            return False
        if user.is_staff:
            return True
        if user.is_customer:
            return ticket.customer == user
        if user.is_contractor:
            return ticket.contractor == user
        if user.is_operator:
            operator: Operator = user.get_role_user()
            if ticket.creator == user:
                return True
            return ticket.customer in operator.get_customers()
        return ticket.creator == user


class AccessOperatorMixin(UserPassesTestMixin):
    def test_func(self):
        user: User = self.request.user
        if user.is_anonymous:
            return False
        if user.is_staff:
            return True
        if user.is_has_operator_access:
            return True
        return False


class AccessAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        user: User = self.request.user
        if user.is_staff:
            return True
        get_author_method = getattr(self, "get_author", None)
        if not get_author_method:
            raise AttributeError("Object must have get_author method")
        author = get_author_method()
        if author is None:
            return False
        return author == user
