import json
import os
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest


def _docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        subprocess.run(
            ["docker", "compose", "version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


def _wait_for_port(host: str, port: int, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(0.5)
    raise TimeoutError(f"Timed out waiting for {host}:{port}")


def _run_compose(compose_file: Path, args: list[str]) -> None:
    subprocess.run(
        ["docker", "compose", "-f", str(compose_file), *args],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


@pytest.mark.integration
def test_rabbitmq_handoff_with_mock_agents():
    if os.getenv("RUN_INTEGRATION_TESTS") != "1":
        pytest.skip("Set RUN_INTEGRATION_TESTS=1 to run docker integration tests.")
    if not _docker_available():
        pytest.skip("Docker (with compose plugin) is not available.")

    compose_file = Path(__file__).resolve().parent / "docker-compose.rabbitmq.yml"
    artifacts_dir = Path(__file__).resolve().parent / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    received_path = artifacts_dir / "received.json"
    if received_path.exists():
        received_path.unlink()

    from app.messaging.orchestrator import Orchestrator

    orch = None
    thread = None

    try:
        _run_compose(compose_file, ["up", "-d", "rabbitmq"])
        _wait_for_port("localhost", 5673, timeout=60.0)

        orch = Orchestrator(amqp_url="amqp://user:password@localhost:5673/")
        thread = threading.Thread(
            target=orch.consume,
            kwargs={"incoming_queue": "incoming_tasks"},
            daemon=True,
        )
        thread.start()

        _run_compose(compose_file, ["up", "-d", "mock_receiver", "mock_sender"])

        deadline = time.time() + 60
        while time.time() < deadline:
            if received_path.exists():
                payload = json.loads(received_path.read_text(encoding="utf-8"))
                assert payload == {"coord": "compute"}
                break
            time.sleep(0.5)
        else:
            raise AssertionError("No message received by mock receiver")

    finally:
        if orch and orch._channel:
            try:
                orch._channel.stop_consuming()
            except Exception:
                pass
        if orch:
            orch.close()
        if thread:
            thread.join(timeout=5)
        _run_compose(compose_file, ["down", "-v"])
