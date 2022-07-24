import json
import os
import urllib.parse

import httpx
from aioredis import Redis
from fastapi import BackgroundTasks


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

