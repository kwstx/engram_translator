import pika
import json
import logging
from typing import Any, Dict, Optional
from app.core.config import settings
from app.core.translator import TranslatorEngine

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Orchestration engine for task handoffs using RabbitMQ.
    Handles listening on incoming queues, translating messages using TranslatorEngine,
    and forwarding them to agent-specific queues.
    """

    def __init__(self, amqp_url: Optional[str] = None):
        """
        Initializes the Orchestrator with a RabbitMQ connection URL and TranslatorEngine.
        """
        self.amqp_url = amqp_url or settings.RABBIT_URL
        self.translator = TranslatorEngine()
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None

    def _connect(self):
        """
        Establishes a blocking connection and channel if not already connected.
        """
        if not self._connection or self._connection.is_closed:
            try:
                parameters = pika.URLParameters(self.amqp_url)
                self._connection = pika.BlockingConnection(parameters)
                self._channel = self._connection.channel()
                logger.info(f"Successfully connected to RabbitMQ at {self.amqp_url}")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
                raise

    def publish_translated(self, target_agent_id: str, message: Dict[str, Any]):
        """
        Publishes a translated message to a queue named 'agent-<uuid>-queue'.
        Uses persistent delivery mode to prevent message loss.
        """
        self._connect()
        queue_name = f"agent-{target_agent_id}-queue"
        
        # Ensure the target queue exists and is durable
        self._channel.queue_declare(queue=queue_name, durable=True)
        
        self._channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message, default=str),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        logger.info(f"Published translated message to {queue_name}")

    def consume(self, incoming_queue: str = "incoming_tasks"):
        """
        Listens on a general incoming queue, translates, and forwards messages.
        Implements manual acknowledgments for reliability.
        """
        self._connect()
        self._channel.queue_declare(queue=incoming_queue, durable=True)
        
        # Fair dispatch: process one message at a time
        self._channel.basic_qos(prefetch_count=1)
        
        def callback(ch, method, properties, body):
            logger.info(f"Received raw message from {incoming_queue}")
            try:
                payload = json.loads(body.decode())
                
                # Expected payload structure:
                # {
                #   "source_message": {...},
                #   "source_protocol": "A2A",
                #   "target_protocol": "MCP",
                #   "target_agent_id": "uuid-..."
                # }
                
                source_message = payload.get("source_message")
                source_protocol = payload.get("source_protocol")
                target_protocol = payload.get("target_protocol")
                target_agent_id = payload.get("target_agent_id")
                
                if not all([source_message, source_protocol, target_protocol, target_agent_id]):
                    logger.warning("Message dropped: Missing required fields (source_message, protocols, or target_agent_id)")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                # Perform translation
                translated_message = self.translator.translate(
                    source_message, 
                    source_protocol, 
                    target_protocol
                )
                
                # Forward the translated message to the target agent
                self.publish_translated(target_agent_id, translated_message)
                
                # Acknowledge receipt after successful forwarding
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Successfully processed and forwarded message for agent {target_agent_id}")
                
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                # Nack message. Don't requeue if it's a permanent translation error to avoid infinite loops.
                # In production, this should go to a Dead Letter Queue (DLQ).
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        self._channel.basic_consume(queue=incoming_queue, on_message_callback=callback)
        logger.info(f"Orchestrator started. Listening on queue: {incoming_queue}")
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Orchestrator stopping...")
            self.close()

    def close(self):
        """
        Closes the RabbitMQ connection.
        """
        if self._connection and self._connection.is_open:
            self._connection.close()
            logger.info("RabbitMQ connection closed.")

if __name__ == "__main__":
    # Basic execution block for manual testing/running
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    orchestrator = Orchestrator()
    try:
        orchestrator.consume()
    except Exception as exc:
        logger.critical(f"Orchestrator fatal error: {exc}")
