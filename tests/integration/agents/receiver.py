import json
import os
import time
import pika


def build_url() -> str:
    user = os.getenv("RABBITMQ_USER", "user")
    password = os.getenv("RABBITMQ_PASS", "password")
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port = os.getenv("RABBITMQ_PORT", "5672")
    return f"amqp://{user}:{password}@{host}:{port}/"


def connect_with_retry(url: str, attempts: int = 30, delay: float = 1.0):
    last_exc = None
    for _ in range(attempts):
        try:
            params = pika.URLParameters(url)
            return pika.BlockingConnection(params)
        except Exception as exc:
            last_exc = exc
            time.sleep(delay)
    raise RuntimeError(f"Failed to connect to RabbitMQ: {last_exc}")


def main() -> None:
    url = build_url()
    conn = connect_with_retry(url)
    channel = conn.channel()
    queue_name = "agent-mock-receiver-queue"
    channel.queue_declare(queue=queue_name, durable=True)

    deadline = time.time() + 60
    while time.time() < deadline:
        method, _, body = channel.basic_get(queue=queue_name, auto_ack=False)
        if method:
            payload = json.loads(body.decode())
            channel.basic_ack(delivery_tag=method.delivery_tag)

            with open("/artifacts/received.json", "w", encoding="utf-8") as fh:
                json.dump(payload, fh)

            conn.close()
            return
        time.sleep(0.5)

    conn.close()
    raise SystemExit("Timed out waiting for message")


if __name__ == "__main__":
    main()
