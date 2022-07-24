import typing

import aio_pika
import aioredis
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel
from aioredis import Redis
from yarl import URL


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class RedisHandler(metaclass=SingletonMeta):
    url: str = None

    def __init__(self):
        self._redis: typing.Optional[Redis] = None

    def connect(self, url: str):
        self.url = url
        self._redis = aioredis.from_url(url)

    async def disconnect(self):
        await self._redis.close()

    async def get_conn(self) -> aioredis.Redis:
        assert self.url is not None, 'Call init(url) first'
        async with self._redis.client() as conn:
            yield conn


class RabbitHandler(metaclass=SingletonMeta):
    url: URL = None

    def __init__(self):
        self._rabbit: typing.Optional[AbstractRobustConnection] = None

    async def connect(self, url: URL):
        self.url = url
        self._rabbit = await aio_pika.connect_robust(url)

    async def disconnect(self):
        await self._rabbit.close()

    async def get_conn(self) -> AbstractRobustChannel:
        assert self._rabbit is not None, 'Call await connect(url) first'
        return await self._rabbit.channel()