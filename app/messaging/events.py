import aio_pika
import json
import asyncio
from app.core.config import settings
from typing import Optional, Any, Callable

class RabbitMQManager:
    def __init__(self, url: str):
        self.url = url
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        print(f"Connected to RabbitMQ: {self.url}")

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def publish(self, routing_key: str, message: Any, exchange_name: str = ""):
        if not self.channel:
            await self.connect()
        
        exchange = await self.channel.get_exchange(exchange_name)
        await exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=routing_key
        )

    async def consume(self, queue_name: str, callback: Callable):
        if not self.channel:
            await self.connect()
        
        queue = await self.channel.declare_queue(queue_name, auto_delete=False)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    payload = json.loads(message.body.decode())
                    await callback(payload)

rabbitmq = RabbitMQManager(settings.RABBIT_URL)
