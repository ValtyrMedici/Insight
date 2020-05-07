from InsightUtilities import ConfigLoader
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from functools import partial
import InsightExc
import InsightLogger


class AbstractBaseClient(object):
    def __init__(self, config_class, thread_pool):
        self.lg = InsightLogger.InsightLogger.get_logger('Cache.Client', 'Cache.log', child=True)
        self.config: ConfigLoader = config_class
        self.loop = asyncio.get_event_loop()
        self.tp: ThreadPoolExecutor = thread_pool

    async def get(self, key_str: str) -> dict:
        raise InsightExc.Subsystem.NoRedis

    async def set(self, key_str: str, ttl: int, data_dict: dict):
        raise InsightExc.Subsystem.NoRedis

    def _serialize(self, obj: dict):
        s = json.dumps(obj)
        return s

    async def serialize(self, obj: dict) -> str:
        return await self.loop.run_in_executor(self.tp, partial(self._serialize, obj))

    def _derialize(self, obj: str) -> dict:
        d = json.loads(obj)
        return d

    async def deserialize(self, obj: str) -> dict:
        return await self.loop.run_in_executor(self.tp, partial(self._derialize, obj))

    async def get_ttl(self, key_str: str) -> int:
        raise InsightExc.Subsystem.NoRedis
