import aioredis


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
        self._redis = None

    def init(self, url: str):
        self.url = url
        self._redis = aioredis.from_url(url)

    async def get_conn(self) -> aioredis.Redis:
        assert self.url is not None, 'Call init(url) first'
        async with self._redis.client() as conn:
            yield conn