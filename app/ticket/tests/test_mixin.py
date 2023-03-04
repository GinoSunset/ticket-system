import pytest

from ticket.mixin import AccessAuthorMixin


class TestAccessAuthorMixin:
    class MockView(AccessAuthorMixin):
        def get_author(self):
            return self.author

        def __init__(self, author, request=None):
            self.author = author
            self.request = request

        def get_object(self):
            return self

    @pytest.mark.django_db
    def test_access_author_mixin(self, rf, user_factory):
        user = user_factory()
        request = rf.get("/")
        request.user = user
        view = self.MockView(author=user, request=request)
        assert view.test_func()

    @pytest.mark.django_db
    def test_access_author_mixin_staff_user(self, rf, user_factory):
        user = user_factory(is_staff=True)
        request = rf.get("/")
        request.user = user
        view = self.MockView(author=None, request=request)
        assert view.test_func()

    @pytest.mark.django_db
    def test_non_access_author_mixin_(self, rf, user_factory):
        user = user_factory()
        user1 = user_factory()
        request = rf.get("/")
        request.user = user
        view = self.MockView(author=user1, request=request)
        assert not view.test_func()
