import time
import asyncio
from threading import Thread

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class BaseParser(object):
    _BEFORE_PARSE_MIDDLEWARE_LIST = []
    _AFTER_PARSE_MIDDLEWARE_LIST = []

    def __init__(self, mission_queue, parse_queue, href_pool):
        self.mission_queue = mission_queue
        self.parse_queue = parse_queue
        self.href_pool = href_pool
        self.meta_url = None
        self.url_pattern = None
        self.parse_loop = asyncio.new_event_loop()

    def pre_process(self, response_object):
        """Method for processing the response content into content object,
        which could be achieved by RegEx, BeautifulSoup or PyQuery."""
        return response_object

    async def parse_page(self, response_content):
        content_object = self.pre_process(response_content)
        extract_data_task = asyncio.ensure_future(self.extract_data(content_object), loop=self.parse_loop)
        asyncio.run_coroutine_threadsafe(await extract_data_task, loop=self.parse_loop)

    async def extract_data(self, content_object) -> None:
        """extract data from content"""
        raise NotImplementedError

    @staticmethod
    def _start_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def conquer(self):
        t = Thread(target=self._start_loop, args=(self.parse_loop,))
        t.setDaemon(True)
        t.start()
        try:
            while 1:
                if self.parse_queue.queue_size == 0:
                    time.sleep(10)
                else:
                    html_content = self.parse_queue.dequeue()
                    if html_content:
                        asyncio.run_coroutine_threadsafe(self.parse_page(html_content), loop=self.parse_loop)
        except KeyboardInterrupt:
            self.mission_queue.serialize()
            self.href_pool.serialize()
        finally:
            pass


class IncreasingParser(object):
    def __init__(self, mission_queue, parse_queue, href_pool):
        self.mission_queue = mission_queue
        self.parse_queue = parse_queue
        self.href_pool = href_pool
        self.url_pattern = None
        self.parse_loop = asyncio.new_event_loop()

    def pre_process(self, response_object):
        """Method for processing the response content into content object,
        which could be achieved by RegEx, BeautifulSoup or PyQuery."""
        return response_object

    async def parse_page(self, response_content):
        content_object = self.pre_process(response_content)

        extract_data_task = asyncio.ensure_future(self.extract_data(content_object), loop=self.parse_loop)
        asyncio.run_coroutine_threadsafe(await extract_data_task, loop=self.parse_loop)

        process_task = asyncio.ensure_future(self.extract_sub_href(content_object), loop=self.parse_loop)
        asyncio.run_coroutine_threadsafe(await process_task, loop=self.parse_loop)

    def go_forward(self, content_object) -> bool:
        """return whether go forward"""
        raise NotImplementedError

    def extract_sub_list(self, content_object) -> list:
        """return sub href list"""
        raise NotImplementedError

    async def extract_sub_href(self, content_object):
        sub_mission_list = self.extract_sub_list(content_object)
        if self.go_forward(content_object):
            for mission in sub_mission_list:
                if not self.href_pool.is_duplicate(mission.unique_tag):
                    self.mission_queue.enqueue(mission.serialize())

    async def extract_data(self, content_object):
        """extract data from content"""
        raise NotImplementedError

    @staticmethod
    def _start_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def conquer(self):
        t = Thread(target=self._start_loop, args=(self.parse_loop,))
        t.setDaemon(True)
        t.start()
        try:
            while 1:
                if self.parse_queue.queue_size == 0:
                    time.sleep(10)
                else:
                    html_content = self.parse_queue.dequeue()
                    if html_content:
                        asyncio.run_coroutine_threadsafe(self.parse_page(html_content), loop=self.parse_loop)
        except KeyboardInterrupt:
            self.mission_queue.serialize()
            self.href_pool.serialize()
        finally:
            pass
