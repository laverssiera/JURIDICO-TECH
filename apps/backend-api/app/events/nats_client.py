import asyncio
import json
import os

from app.events.envelope import build_event_envelope

_nc = None
_js = None
_lock = asyncio.Lock()


async def _connect() -> tuple[object | None, object | None]:
    global _nc, _js

    if _nc is not None and _nc.is_connected:
        return _nc, _js

    async with _lock:
        if _nc is not None and _nc.is_connected:
            return _nc, _js

        nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
        stream_name = os.getenv("NATS_STREAM", "LEGAL_EVENTS")

        try:
            from nats.aio.client import Client as NATS
            from nats.js.errors import BadRequestError

            _nc = NATS()
            await _nc.connect(servers=[nats_url], connect_timeout=1)
            _js = _nc.jetstream()
            try:
                await _js.add_stream(name=stream_name, subjects=["legal.>"])
            except BadRequestError:
                # Stream already exists.
                pass
            return _nc, _js
        except Exception:
            _nc = None
            _js = None
            return None, None


async def publish_event(subject: str, payload: dict) -> dict:
    envelope = build_event_envelope(payload=payload)
    _, js = await _connect()

    if js is None:
        return {
            "status": "fallback_queued",
            "subject": subject,
            "event": envelope,
        }

    try:
        ack = await js.publish(subject, json.dumps(envelope).encode("utf-8"))
        return {
            "status": "published",
            "subject": subject,
            "stream": ack.stream,
            "sequence": ack.seq,
            "event": envelope,
        }
    except Exception:
        return {
            "status": "fallback_queued",
            "subject": subject,
            "event": envelope,
        }
