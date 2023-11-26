def test_exist_storage_list_view(client):
    response = client.get(reverse("storage-list"))
    assert response.status_code == 200
