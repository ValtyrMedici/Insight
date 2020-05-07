from InsightSubsystems.SubsystemBase import SubsystemBase
from InsightSubsystems.Cache.Clients import RedisClient, NoRedisClient
from InsightSubsystems.Cache import CacheEndpoint
import sys
from concurrent.futures import ThreadPoolExecutor
import InsightLogger


class CacheManager(SubsystemBase):
    def __init__(self, subsystemloader):
        super().__init__(subsystemloader)
        self.lg_cache = InsightLogger.InsightLogger.get_logger('Cache.Manager', 'Cache.log', child=True)
        self.tp = ThreadPoolExecutor(max_workers=5)
        self.client = NoRedisClient.NoRedisClient(self.config, self.tp)
        self.MostExpensiveKMs = CacheEndpoint.MostExpensiveKMs(cache_manager=self)
        self.KMStats = CacheEndpoint.KMStats(cache_manager=self)
        self.MostExpensiveKMsEmbed = CacheEndpoint.MostExpensiveKMsEmbed(cache_manager=self)
        self.CharacterNameToID = CacheEndpoint.CharacterNameToID(cache_manager=self)
        self.BulkCharacterNameToID = CacheEndpoint.BulkCharacterNameToID(cache_manager=self)
        self.LastShip = CacheEndpoint.LastShip(cache_manager=self)

    async def start_subsystem(self):
        try:
            redis = RedisClient.RedisClient(self.config, self.tp)
            if await redis.establish_connection():
                self.client = redis
                print("Redis connection established.")
            else:
                sys.stderr.write("Insight is operating without Redis. Please connect Insight to Redis for all functions"
                                 " to properly work.")
        except Exception as ex:
            print(ex)

    async def stop_subsystem(self):
        self.client.tp.shutdown(wait=True)

    async def get_cache(self, key_str: str) -> dict:
        st = InsightLogger.InsightLogger.time_start()
        data = await self.client.get(key_str)
        ttl = await self.client.get_ttl(key_str)
        query_ms = InsightLogger.InsightLogger.time_log(self.lg_cache, st, 'get "{}" ttl: {}'.format(key_str, ttl),
                                                        warn_higher=2000, seconds=False)
        data["redis"] = {
            "ttl": ttl,
            "queryms": query_ms,
            "cacheHit": True
        }
        return data

    async def set_cache(self, key_str: str, ttl: int, data_dict: dict):
        await self.client.set(key_str, ttl, data_dict)

    async def set_and_get_cache(self, key_str: str, ttl: int, data_dict: dict, operation_start_time):
        await self.set_cache(key_str, ttl, data_dict)
        d = await self.get_cache(key_str)
        ttl = d["redis"]["ttl"]
        query_ms = InsightLogger.InsightLogger.time_log(self.lg_cache, operation_start_time,
                                                        'set+get "{}" ttl: {}'.format(key_str, ttl), warn_higher=5000,
                                                        seconds=False)
        d["redis"]["queryms"] = query_ms
        d["redis"]["cacheHit"] = False
        return d