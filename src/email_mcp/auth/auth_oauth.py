from __future__ import annotations

from typing import Any

from mcp.server.auth.provider import OAuthAuthorizationServerProvider


class PlaceholderOAuthProvider(OAuthAuthorizationServerProvider[Any, Any, Any]):
    """Placeholder OAuth provider for wiring custom OAuth 2.1 integrations."""

    async def get_client(self, client_id: str):  # pragma: no cover
        raise NotImplementedError("OAuth provider integration not configured.")

    async def register_client(self, client_info):  # pragma: no cover
        raise NotImplementedError("OAuth provider integration not configured.")

    async def authorize(self, client, params):  # pragma: no cover
        raise NotImplementedError("OAuth provider integration not configured.")

    async def exchange_authorization_code(self, client, auth_code):  # pragma: no cover
        raise NotImplementedError("OAuth provider integration not configured.")

    async def load_authorization_code(self, client, code):  # pragma: no cover
        raise NotImplementedError("OAuth provider integration not configured.")

    async def load_refresh_token(self, client, refresh_token):  # pragma: no cover
        raise NotImplementedError("OAuth provider integration not configured.")

    async def exchange_refresh_token(self, client, refresh_token, scopes):  # pragma: no cover
        raise NotImplementedError("OAuth provider integration not configured.")

    async def load_access_token(self, token):  # pragma: no cover
        raise NotImplementedError("OAuth provider integration not configured.")

    async def revoke_token(self, token):  # pragma: no cover
        raise NotImplementedError("OAuth provider integration not configured.")
