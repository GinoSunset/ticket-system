import pytest
import uuid
from django.urls import reverse


@pytest.mark.django_db
def test_set_tg_id_exist_user_by_token(client, user_factory):
    user = user_factory()
    tg_id = "123123123"
    url = reverse("set-user-telegram-id", kwargs={"token": user.token})
    response = client.post(url, {"telegram_id": tg_id})
    assert response.status_code == 200
    res_user = response.json()
    assert res_user["user"]["id"] == user.id
    user.refresh_from_db()
    assert user.telegram_id == tg_id


@pytest.mark.django_db
def test_get_user_by_token_return_if_user_not_exist(client, user_factory):
    url = reverse("set-user-telegram-id", kwargs={"token": uuid.uuid4()})
    response = client.post(url, {"telegram_id": "123123123"})
    assert response.status_code == 404
