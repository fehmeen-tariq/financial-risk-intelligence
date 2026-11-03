"""Small client for the SEC EDGAR Company Facts JSON endpoint."""

from __future__ import annotations

import os
import re
from typing import Any

import requests

_COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
_CIK_PATTERN = re.compile(r"^\d{1,10}$")


class CompanyFactsClient:
    """Fetch a company's XBRL facts from SEC EDGAR.

    The SEC requires a descriptive User-Agent with contact information. It can be
    provided directly or through ``SEC_USER_AGENT``. A requests session may be
    injected to simplify testing and connection reuse.
    """

    def __init__(
        self,
        user_agent: str | None = None,
        timeout: float | None = None,
        session: requests.Session | None = None,
    ) -> None:
        agent = user_agent or os.getenv("SEC_USER_AGENT")
        if not agent or not agent.strip():
            raise ValueError(
                "Set SEC_USER_AGENT to a descriptive application name and contact email."
            )
        configured_timeout = os.getenv("SEC_API_TIMEOUT", "20")
        self._timeout = timeout if timeout is not None else float(configured_timeout)
        if self._timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        self._session = session or requests.Session()
        self._headers = {"User-Agent": agent.strip(), "Accept": "application/json"}

    def get_company_facts(self, cik: str | int) -> dict[str, Any]:
        """Return the SEC Company Facts document for a CIK (zero-padded to 10 digits)."""
        cik_text = str(cik).strip()
        if not _CIK_PATTERN.fullmatch(cik_text):
            raise ValueError("CIK must contain between 1 and 10 digits")
        padded_cik = cik_text.zfill(10)
        response = self._session.get(
            _COMPANY_FACTS_URL.format(cik=padded_cik),
            headers=self._headers,
            timeout=self._timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("facts"), dict):
            raise ValueError("SEC Company Facts response is missing the expected 'facts' object")
        return payload
