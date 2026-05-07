from collections.abc import Callable

from fastapi import Request, Response


class TenantMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        tenant = request.headers.get("x-tenant-id", "public")
        scope["state"] = {**scope.get("state", {}), "tenant": tenant}
        await self.app(scope, receive, send)
