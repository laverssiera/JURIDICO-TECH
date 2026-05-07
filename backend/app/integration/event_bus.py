from __future__ import annotations

import asyncio
from collections import defaultdict
import json
import logging
import os
from typing import Any, Callable

from app.integration.legal_event_registry import (
    normalize_event_name,
    subject_for_event,
    subscription_subjects_for_event,
)


Handler = Callable[[dict[str, Any]], dict[str, Any]]


logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Handler]] = defaultdict(list)
        self._nats_client: Any | None = None
        self._nats_loop: asyncio.AbstractEventLoop | None = None
        self._subscribed_subjects: set[str] = set()
        self._nats_connect_retries = int(os.getenv("NATS_CONNECT_RETRIES", "3"))
        self._nats_retry_delay_ms = int(os.getenv("NATS_RETRY_DELAY_MS", "250"))

    def _publish_subject_for(self, event_name: str) -> str:
        return subject_for_event(event_name)

    def _subscription_subjects_for(self, event_name: str) -> list[str]:
        return subscription_subjects_for_event(event_name)

    def _schedule(self, coro: asyncio.Future, description: str) -> None:
        if not self._nats_loop:
            return
        future = asyncio.run_coroutine_threadsafe(coro, self._nats_loop)

        def _log_result(done_future) -> None:
            try:
                done_future.result()
            except Exception as exc:
                logger.warning("NATS async task failed during %s: %s", description, exc)

        future.add_done_callback(_log_result)

    def _publish_local(self, event_name: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        handlers = self._subscribers.get(event_name, [])
        return [handler(payload) for handler in handlers]

    async def _subscribe_remote(self, event_name: str) -> None:
        if not self._nats_client:
            return
        for subject in self._subscription_subjects_for(event_name):
            if subject in self._subscribed_subjects:
                continue

            async def handler(message, subscribed_event_name: str = event_name, subscribed_subject: str = subject) -> None:
                try:
                    payload = json.loads(message.data.decode("utf-8"))
                except json.JSONDecodeError as exc:
                    logger.warning("Invalid JSON received from subject %s: %s", subscribed_subject, exc)
                    return
                logger.info("NATS message received on %s", subscribed_subject)
                self._publish_local(normalize_event_name(subscribed_event_name), payload)

            await self._nats_client.subscribe(subject, cb=handler)
            self._subscribed_subjects.add(subject)
            logger.info("Subscribed to NATS subject %s", subject)

    async def startup(self) -> bool:
        nats_url = os.getenv("NATS_URL")
        if not nats_url:
            logger.info("NATS disabled; using in-memory event bus only")
            return False

        try:
            import nats
        except ImportError:
            logger.warning("NATS_URL configured but nats-py is not installed; using local event bus fallback")
            return False

        for attempt in range(1, self._nats_connect_retries + 1):
            try:
                self._nats_client = await nats.connect(
                    servers=[nats_url],
                    connect_timeout=2,
                    max_reconnect_attempts=self._nats_connect_retries,
                    reconnect_time_wait=self._nats_retry_delay_ms / 1000,
                    disconnected_cb=lambda: logger.warning("Disconnected from NATS broker"),
                    reconnected_cb=lambda: logger.info("Reconnected to NATS broker"),
                    error_cb=lambda exc: logger.warning("NATS client error: %s", exc),
                    closed_cb=lambda: logger.info("NATS connection closed"),
                )
                break
            except Exception as exc:
                self._nats_client = None
                logger.warning(
                    "Failed to connect to NATS at %s (attempt %s/%s): %s",
                    nats_url,
                    attempt,
                    self._nats_connect_retries,
                    exc,
                )
                if attempt < self._nats_connect_retries:
                    await asyncio.sleep(self._nats_retry_delay_ms / 1000)

        if not self._nats_client:
            logger.warning("Using local event bus fallback after NATS connection failures")
            return False

        self._nats_loop = asyncio.get_running_loop()
        for event_name in self._subscribers:
            await self._subscribe_remote(event_name)
        logger.info("NATS event bus started successfully")
        return True

    async def shutdown(self) -> None:
        if not self._nats_client:
            return
        try:
            await self._nats_client.drain()
        finally:
            logger.info("NATS event bus shutdown complete")
            self._nats_client = None
            self._nats_loop = None
            self._subscribed_subjects.clear()

    def subscribe(self, event_name: str, handler: Handler) -> None:
        normalized_event_name = normalize_event_name(event_name)
        if handler not in self._subscribers[normalized_event_name]:
            self._subscribers[normalized_event_name].append(handler)

        if self._nats_client and self._nats_loop:
            self._schedule(self._subscribe_remote(normalized_event_name), f"subscribe {normalized_event_name}")

    def publish(self, event_name: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        normalized_event_name = normalize_event_name(event_name)
        executions = self._publish_local(normalized_event_name, payload)

        if self._nats_client and self._nats_loop:
            async def remote_publish() -> None:
                if not self._nats_client:
                    return
                await self._nats_client.publish(
                    self._publish_subject_for(normalized_event_name),
                    json.dumps(payload, ensure_ascii=True).encode("utf-8"),
                )
                logger.info("Published event %s to NATS", normalized_event_name)

            self._schedule(remote_publish(), f"publish {normalized_event_name}")

        return executions


event_bus = EventBus()
