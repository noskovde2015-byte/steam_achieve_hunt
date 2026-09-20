import json
import aio_pika
from app.core.config import settings

QUEUE_NAME = "user_sync_queue"


async def publish_sync_task(user_id: int) -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq.url)

    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(QUEUE_NAME, durable=True)

        message_body = json.dumps({"user_id": user_id}).encode()

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=QUEUE_NAME,
        )
