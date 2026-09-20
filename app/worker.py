import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.core.config import settings
from app.core.models.db_helper import db_helper
from app.game_info.games_service import sync_all_user_games
from app.messaging.rabbitmq import QUEUE_NAME

logger = logging.getLogger(__name__)


async def handle_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        data = json.loads(message.body.decode())
        user_id = data["user_id"]

        async with db_helper.session_factory() as session:
            await sync_all_user_games(session=session, user_id=user_id)


async def main() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq.url)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(QUEUE_NAME, durable=True)

        await queue.consume(handle_message)

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
