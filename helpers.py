import datetime
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
    """
    Set data to key in redis with given expiration time
    """
    await redis.set(key, data, ex=ex)


async def update_cached_data(redis: Redis, key: str, data: str | bytes):
    """
    Update data of key and keep remaining expiration time
    """
    await redis.set(key, data, keepttl=True)


async def get_events_cached(redis: Redis, tasks: BackgroundTasks) -> list[dict]:
    """
    Get events from cache if possible
    """
    # get from cache
    events = await redis.get(os.getenv('EVENTS_REDIS_KEY'))
    if events is not None:
        # filter and update if changed
        now = datetime.datetime.now()
        events_filtered = list(filter(lambda e: e['deadline'] > now, json.loads(events)))
        if len(events_filtered) < len(events):
            tasks.add_task(update_cached_data, redis, os.getenv('EVENTS_REDIS_KEY'), json.dumps(events_filtered))
        return events_filtered

    # if got nothing from cache - get from line-provider service
    async with httpx.AsyncClient() as client:  # type: httpx.AsyncClient
        response = await client.get(urllib.parse.urljoin(os.getenv('EVENTS_API_URL'), '/events?current=true'))

    # if got non empty data - update cache
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
            