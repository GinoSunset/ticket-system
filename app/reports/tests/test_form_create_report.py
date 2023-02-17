import pytest
from reports.forms import ReportForm


@pytest.mark.django_db
def test_create_report_form():
    form = ReportForm(
        data={
            "start_date": "2020-01-01",
            "end_date": "2020-01-31",
        }
    )

    assert form.is_valid() is True
    report = form.save()
    assert report.file is not None


@pytest.mark.django_db
def test_create_report_by_client(client, operator_factory):
    user = operator_factory()
    client.force_login(user)
    response = client.post(
        "/reports/create/",
        data={
            "start_date": "2020-01-01",
            "end_date": "2020-01-31",
        },
    )

    assert response.status_code == 302
    assert response.url == "/reports/"
    assert response.client.session.get("report") is not None
