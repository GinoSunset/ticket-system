import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


def test_command_success(monkeypatch, tmp_path, capsys):
    # process_response returns a dict (single task)
    task = {"sys_id": "abc123", "number": "156"}

    monkeypatch.setattr("ticket.management.commands.add_itsm_ticket.get_with_auth_header", lambda url: DummyResponse({"status": "OK", "data": task}))
    monkeypatch.setattr("ticket.management.commands.add_itsm_ticket.process_response", lambda res: res.json()["data"] if isinstance(res.json(), dict) else res.json())
    monkeypatch.setattr("ticket.management.commands.add_itsm_ticket.create_itsm_task", lambda t: True)

    # Should not raise and should print success
    call_command("add_itsm_ticket", "abc123")


def test_command_already_exists(monkeypatch):
    task = {"sys_id": "abc123", "number": "156"}

    monkeypatch.setattr("ticket.management.commands.add_itsm_ticket.get_with_auth_header", lambda url: DummyResponse({"status": "OK", "data": task}))
    monkeypatch.setattr("ticket.management.commands.add_itsm_ticket.process_response", lambda res: res.json()["data"] if isinstance(res.json(), dict) else res.json())
    monkeypatch.setattr("ticket.management.commands.add_itsm_ticket.create_itsm_task", lambda t: False)

    # Should not raise; prints warning
    call_command("add_itsm_ticket", "abc123")


def test_command_bad_format(monkeypatch):
    # process_response returns unexpected type
    monkeypatch.setattr("ticket.management.commands.add_itsm_ticket.get_with_auth_header", lambda url: DummyResponse({"status": "ERROR"}))
    monkeypatch.setattr("ticket.management.commands.add_itsm_ticket.process_response", lambda res: (_ for _ in ()).throw(ValueError("bad")))

    with pytest.raises(CommandError):
        call_command("add_itsm_ticket", "abc123")
