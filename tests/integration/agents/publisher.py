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
    channel.queue_declare(queue="incoming_tasks", durable=True)

    payload = {
        "source_message": {"protocol": "A2A", "data": {"task": "compute"}},
        "source_protocol": "A2A",
        "target_protocol": "MCP",
        "target_agent_id": "mock-receiver",
    }

    channel.basic_publish(
        exchange="",
        routing_key="incoming_tasks",
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2),
    )

    conn.close()


if __name__ == "__main__":
    main()
