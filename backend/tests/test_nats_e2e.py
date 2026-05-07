from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
import os
import shutil
import socket
import subprocess
import time
from uuid import uuid4

import pytest

import nats

from app.consumers.legal_consumer import LegalConsumer
from core_dna.compiled import legal_pb2


UTC = timezone.utc
CONTAINER_NAME = "juridicotech-nats-e2e"


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


async def _wait_for_nats(nats_url: str, timeout_seconds: float = 12) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            nc = await nats.connect(nats_url, connect_timeout=1)
            await nc.drain()
            return
        except Exception as exc:  # pragma: no cover - exercised only in env-dependent loop
            last_error = exc
            await asyncio.sleep(0.2)

    raise RuntimeError(f"NATS did not become ready at {nats_url}: {last_error}")


def _docker_available() -> bool:
    return shutil.which("docker") is not None


@pytest.mark.skipif(os.getenv("RUN_NATS_E2E") != "1", reason="Set RUN_NATS_E2E=1 to run JetStream E2E tests")
def test_nats_jetstream_e2e_deal_created_blocks_without_nda():
    if not _docker_available():
        pytest.skip("docker is required for NATS E2E test")

    host_port = _find_free_port()
    nats_url = f"nats://127.0.0.1:{host_port}"

    subprocess.run(["docker", "rm", "-f", CONTAINER_NAME], check=False, capture_output=True)
    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            CONTAINER_NAME,
            "-p",
            f"{host_port}:4222",
            "nats:2.10",
            "-js",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    async def run_scenario() -> dict:
        await _wait_for_nats(nats_url)
        nc = await nats.connect(nats_url)
        js = nc.jetstream()

        try:
            await js.add_stream(name="LICEU_EVENTS", subjects=["liceu.events.>"])
        except Exception:
            pass

        consumer = LegalConsumer()
        await consumer.start(nats_url)

        done: asyncio.Future[dict] = asyncio.get_running_loop().create_future()

        async def capture(msg) -> None:
            event = legal_pb2.LegalEvent()
            event.ParseFromString(msg.data)
            if event.event_type in {"legal.blocked", "contract.generated"} and not done.done():
                done.set_result(
                    {
                        "event_type": event.event_type,
                        "entity_id": event.entity_id,
                        "metadata": dict(event.metadata),
                    }
                )

        await js.subscribe("liceu.events.legal.*", durable="juridicotech_capture_e2e", cb=capture)

        event = legal_pb2.LegalEvent(
            event_id=str(uuid4()),
            event_type="deal_created",
            entity_type="deal",
            entity_id="deal_e2e_123",
            user_id="usr_e2e",
            module="ARCHIMEDES_CORE",
            metadata={"event_version": "v1"},
            timestamp=int(datetime.now(UTC).timestamp()),
        )

        await js.publish("liceu.events.deals.created", event.SerializeToString())
        result = await asyncio.wait_for(done, timeout=8)

        await consumer.stop()
        await nc.drain()
        return result

    try:
        result = asyncio.run(run_scenario())
        assert result["event_type"] == "legal.blocked"
        assert result["entity_id"] == "deal_e2e_123"
        assert result["metadata"]["reason"] == "Missing NDA"
        assert result["metadata"]["event_version"] == "v1"
    finally:
        subprocess.run(["docker", "rm", "-f", CONTAINER_NAME], check=False, capture_output=True)
