"""Tests for the SEC Company Facts client using mocked HTTP responses."""

from unittest.mock import Mock

import pytest
import requests

from financial_risk_intelligence.sec import CompanyFactsClient


def mocked_session(payload: object) -> tuple[Mock, Mock]:
    response = Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    session = Mock(spec=requests.Session)
    session.get.return_value = response
    return session, response


def test_fetches_and_returns_company_facts() -> None:
    payload = {"cik": 320193, "entityName": "Apple Inc.", "facts": {"us-gaap": {}}}
    session, _ = mocked_session(payload)
    client = CompanyFactsClient(user_agent="Test Research test@example.com", session=session)

    result = client.get_company_facts(320193)

    assert result == payload
    session.get.assert_called_once_with(
        "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json",
        headers={"User-Agent": "Test Research test@example.com", "Accept": "application/json"},
        timeout=20,
    )


def test_rejects_invalid_cik_before_request() -> None:
    session, _ = mocked_session({"facts": {}})
    client = CompanyFactsClient(user_agent="Test test@example.com", session=session)

    with pytest.raises(ValueError, match="CIK"):
        client.get_company_facts("12-34")
    session.get.assert_not_called()


def test_requires_user_agent() -> None:
    with pytest.raises(ValueError, match="SEC_USER_AGENT"):
        CompanyFactsClient(user_agent="  ")


def test_rejects_unexpected_response_shape() -> None:
    session, _ = mocked_session({"entityName": "Incomplete"})
    client = CompanyFactsClient(user_agent="Test test@example.com", session=session)

    with pytest.raises(ValueError, match="facts"):
        client.get_company_facts("1")


def test_propagates_http_errors() -> None:
    session, response = mocked_session({"facts": {}})
    response.raise_for_status.side_effect = requests.HTTPError("rate limited")
    client = CompanyFactsClient(user_agent="Test test@example.com", session=session)

    with pytest.raises(requests.HTTPError, match="rate limited"):
        client.get_company_facts("1")


def test_loads_configuration_from_dotenv_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    monkeypatch.delenv("SEC_API_TIMEOUT", raising=False)
    (tmp_path / ".env").write_text(
        "SEC_USER_AGENT=Dotenv Test dotenv@example.com\nSEC_API_TIMEOUT=7\n"
    )
    session, _ = mocked_session({"facts": {}})

    client = CompanyFactsClient(session=session)

    assert client._headers["User-Agent"] == "Dotenv Test dotenv@example.com"
    assert client._timeout == 7


def test_environment_variables_override_dotenv_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "SEC_USER_AGENT=Dotenv Test dotenv@example.com\nSEC_API_TIMEOUT=7\n"
    )
    monkeypatch.setenv("SEC_USER_AGENT", "Environment Test env@example.com")
    monkeypatch.setenv("SEC_API_TIMEOUT", "11")
    session, _ = mocked_session({"facts": {}})

    client = CompanyFactsClient(session=session)

    assert client._headers["User-Agent"] == "Environment Test env@example.com"
    assert client._timeout == 11
