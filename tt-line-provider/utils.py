import typing

import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel
from yarl import URL

from models import HasID, HasStatus


Obj = HasID | HasStatus


class DummyDB(list):
    def add(self, obj: Obj):
        self.append(obj)

    def get_all(self):
        return self.copy()

    def get(self, id_: str) -> typing.Optional[Obj]:
        for elem in self:
            if elem.get_id() == id_:
                return elem.copy()
        else:
            return None

    def update(self, id_: str, obj: Obj) -> bool:
        for i in range(len(self)):
            if self[i].get_id() == id_:
                self[i] = obj
                return True
        else:
            return False


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class RabbitHandler(metaclass=SingletonMeta):
    """
    Singleton class to maintain single (or how many necessary) connection
    and access it from anywhere.
    Usage:
    await RabbitHandler().connect(url)
    ...
    await RabbitHandler().get_conn() to acquire channel
    ...
    await RabbitHandler().disconnect()
    """

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