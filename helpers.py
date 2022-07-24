import json
import os
import urllib.parse

import httpx
from aio_pika.abc import AbstractIncomingMessage
from aioredis import Redis
from fastapi import BackgroundTasks
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager

from connections.database import get_session
from models import EventStatusUpdate, Bet


async def cache_data(redis: Redis, key: str, data: str | bytes, ex: int):
    await redis.set(key, data, ex=ex)


async def get_events_cached(redis: Redis, tasks: BackgroundTasks) -> dict:
    events = await redis.get(os.getenv('EVENTS_REDIS_KEY'))
    if events is not None:
        return json.loads(events)

    async with httpx.AsyncClient() as client:  # type: httpx.AsyncClient
        response = await client.get(urllib.parse.urljoin(os.getenv('EVENTS_API_URL'), '/events?current=true'))

    if data := response.json():
        tasks.add_task(cache_data, redis, os.getenv('EVENTS_REDIS_KEY'), response.text, int(os.getenv('EVENTS_REDIS_EX')))

    return data


async def update_bet(message: AbstractIncomingMessage) -> None:
    event = EventStatusUpdate(**json.loads(message.body))

    get_session_ = asynccontextmanager(get_session)
    async with get_session_() as session:  # type: AsyncSession
        expr = select(Bet).where(Bet.event_uid == event.uid)
        bets = (await session.exec(expr)).all()
        for bet in bets:
            bet.status = event.status
            session.add(bet)
        await session.commit()
    await message.ack()
            