from __future__ import annotations

import os
from typing import Awaitable, Callable

from nats.aio.client import Client as NATS


MessageHandler = Callable[[object], Awaitable[None]]


class NATSBus:
    def __init__(self) -> None:
        self.nc = NATS()
        self.connected = False

    async def connect(self, url: str = "nats://localhost:4222") -> None:
        if self.connected:
            return
        await self.nc.connect(url)
        self.connected = True

    async def close(self) -> None:
        if self.connected:
            await self.nc.drain()
            self.connected = False

    async def publish(self, subject: str, data: str) -> None:
        if not self.connected:
            await self.connect(os.getenv("NATS_URL", "nats://localhost:4222"))
        await self.nc.publish(subject, data.encode("utf-8"))

    async def subscribe(self, subject: str, handler: MessageHandler) -> None:
        if not self.connected:
            await self.connect(os.getenv("NATS_URL", "nats://localhost:4222"))
        await self.nc.subscribe(subject, cb=handler)


nats_bus = NATSBus()
