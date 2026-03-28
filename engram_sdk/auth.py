from typing import Any, Dict, Optional

from .communication import EngramTransport
from .exceptions import EngramAuthError


class AuthClient:
    def __init__(self, transport: EngramTransport) -> None:
        self._transport = transport

    def login(self, email: str, password: str) -> str:
        payload = {"username": email, "password": password}
        response = self._transport.request_json(
            "POST",
            "/auth/login",
            data=payload,
            auth=None,
        )
        access_token = response.get("access_token")
        if not access_token:
            raise EngramAuthError("Login response missing access_token.")
        self._transport.set_token(access_token)
        return access_token

    def signup(
        self,
        email: str,
        password: str,
        *,
        user_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self._transport.request_json(
            "POST",
            "/auth/signup",
            json_body={
                "email": email,
                "password": password,
                "user_metadata": user_metadata or {"source": "sdk"},
            },
            auth=None,
        )

    def generate_eat(self) -> str:
        response = self._transport.request_json(
            "POST",
            "/auth/tokens/generate-eat",
            auth="token",
        )
        eat = response.get("eat")
        if not eat:
            raise EngramAuthError("EAT generation failed; missing eat token.")
        self._transport.set_eat(eat)
        return eat

    def set_session_token(self, token: Optional[str]) -> None:
        self._transport.set_token(token)

    def set_eat(self, eat: Optional[str]) -> None:
        self._transport.set_eat(eat)
