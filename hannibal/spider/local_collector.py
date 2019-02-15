import aiohttp
import asyncio
from queue import Queue
from collections import deque
from threading import Thread
from hannibal.util import TrickHelper, Mission

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class LocalCollector(object):
    _BEFORE_COLLECT_MIDDLEWARE_LIST = deque()
    _ERROR_HANDLER_DICT = dict()

    def __init__(self, mission_queue, parse_function, href_pool, seed_mission=None, cache_size=3, *args, **kwargs):
        self.mission_queue = mission_queue
        self.parse_function = parse_function
        self.href_pool = href_pool
        if seed_mission:
            self.mission_queue.enqueue(seed_mission.serialize())
        self.trick_helper = TrickHelper()
        self.collect_loop = asyncio.new_event_loop()
        self.semaphore = asyncio.Semaphore(cache_size, loop=self.collect_loop)
        self.client_session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False, loop=self.collect_loop), loop=self.collect_loop)
        self.collect_queue = Queue(maxsize=cache_size)
        self.end = False

    @staticmethod
    def register_error_handler(code, handler, *args, **kwargs):
        assert isinstance(code, int)
        assert callable(handler)
        LocalCollector._ERROR_HANDLER_DICT[code] = handler

    @staticmethod
    def register_middleware(middleware, *args, **kwargs):
        assert callable(middleware)
        LocalCollector._BEFORE_COLLECT_MIDDLEWARE_LIST.append(middleware)

    async def collect(self, *args, **kwargs):
        with (await self.semaphore):
            mission_str = self.collect_queue.get()
            if isinstance(mission_str, bytes):
                mission_str = mission_str.decode('utf-8')
            mission = Mission.deserialize(mission_str)
            if not mission:
                raise AttributeError("Mission string parsing failed.")
            else:
                for func in LocalCollector._BEFORE_COLLECT_MIDDLEWARE_LIST:
                    func(mission)
                if not self.href_pool.is_duplicate(mission.unique_tag):
                    await self._collect(mission)

    def _insert_url(self, future):
        processed_url = future.result()
        if processed_url:
            self.href_pool.insert(processed_url)

    async def _collect(self, mission):
        url = mission.url
        headers = self.trick_helper.trick()
        async with self.client_session.request(mission.method, url,
                                               **{mission.data_type: mission.data, 'headers': headers})as response:
            process_task = asyncio.ensure_future(self.process_response(response, mission), loop=self.collect_loop)
            process_task.add_done_callback(self._insert_url)
            asyncio.run_coroutine_threadsafe(await process_task, loop=self.collect_loop)

    async def process_response(self, response, mission):
        status_code = int(response.status)
        if 400 < status_code < 600:
            handler = LocalCollector._ERROR_HANDLER_DICT.get(status_code, None)
            if handler:
                handler(response, mission)
            return None
        else:
            await self.parse_function(response, mission)
            return mission.unique_tag

    def _pop_url(self) -> str:
        try:
            url = self.mission_queue.dequeue()
            return url if url else ''
        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def _start_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def conquer(self, limited=False):
        t = Thread(target=self._start_loop, args=(self.collect_loop,))
        t.setDaemon(True)
        t.start()

        try:
            while 1:
                if not self.collect_queue.full():
                    url = self._pop_url()
                    if url:
                        self.collect_queue.put(url)
                    if limited and url == self.mission_queue.endpoint:
                        self.end = True
                        break
                    if url:
                        asyncio.run_coroutine_threadsafe(self.collect(), loop=self.collect_loop)
        except KeyboardInterrupt:
            self.mission_queue.serialize()
            self.href_pool.serialize()
        finally:
            asyncio.run_coroutine_threadsafe(self.client_session.close(), loop=self.collect_loop)
