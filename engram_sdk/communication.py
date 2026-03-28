from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from .exceptions import EngramRequestError, EngramResponseError


class EngramTransport:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 60.0,
        token: Optional[str] = None,
        eat: Optional[str] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._token = token
        self._eat = eat
        self._client = httpx.Client(timeout=timeout)

    @property
    def base_url(self) -> str:
        return self._base_url

    def set_base_url(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def set_token(self, token: Optional[str]) -> None:
        self._token = token

    def set_eat(self, eat: Optional[str]) -> None:
        self._eat = eat

    def _auth_header(self, token: Optional[str]) -> Dict[str, str]:
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def _merge_headers(
        self, base: Optional[Dict[str, str]], extra: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        merged: Dict[str, str] = {}
        if base:
            merged.update(base)
        if extra:
            merged.update(extra)
        return merged

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self._base_url}{path}"

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[str] = "eat",
    ) -> httpx.Response:
        token = None
        if auth == "token":
            token = self._token
        elif auth == "eat":
            token = self._eat

        request_headers = self._merge_headers(headers, self._auth_header(token))
        url = self._build_url(path)
        return self._client.request(
            method,
            url,
            json=json_body,
            data=data,
            headers=request_headers,
        )

    def request_json(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[str] = "eat",
    ) -> Dict[str, Any]:
        response = self.request(
            method,
            path,
            json_body=json_body,
            data=data,
            headers=headers,
            auth=auth,
        )

        if response.status_code >= 400:
            detail = response.text
            try:
                payload = response.json()
                if isinstance(payload, dict):
                    detail = str(payload.get("detail") or payload.get("error") or detail)
            except Exception:
                pass
            raise EngramRequestError(
                f"Engram request failed ({response.status_code}): {detail}"
            )

        try:
            return response.json()
        except Exception as exc:
            raise EngramResponseError(
                f"Engram response was not valid JSON: {exc}"
            ) from exc

    def ping(self) -> bool:
        root_url = self._base_url.replace("/api/v1", "")
        response = self._client.get(root_url, headers=self._auth_header(self._eat or self._token))
        return response.status_code == 200

    def close(self) -> None:
        self._client.close()
