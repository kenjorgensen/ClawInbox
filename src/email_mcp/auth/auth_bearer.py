from __future__ import annotations

from mcp.server.auth.provider import AccessToken, TokenVerifier


class StaticTokenVerifier(TokenVerifier):
    def __init__(self, token: str, scopes: list[str] | None = None) -> None:
        self.token = token
        self.scopes = scopes or []

    async def verify_token(self, token: str) -> AccessToken | None:
        if token != self.token:
            return None
        return AccessToken(token=token, client_id="static", scopes=self.scopes)
