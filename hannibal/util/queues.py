from multiprocessing import Queue
from queue import Empty
from redis import Redis
from hannibal.util.common_utils import Mission
import uuid
import os


class RedisQueue(object):
    def __init__(self, name: str, host: str, pwd: str, port=6379, db=0, limited=False):
        self.name = name
        self._queue = Redis(host=host, port=port, db=db, password=pwd)
        self.limited = limited
        self.endpoint = None

    @property
    def queue_size(self):
        return self._get_queue_size()

    def _get_queue_size(self):
        return self._queue.llen(self.name)

    def enqueue(self, value: str):
        self._queue.rpush(self.name, value)

    def dequeue(self):
        element = self._queue.lpop(self.name)
        return element if element else None

    def init_queue(self, mission_list: list):
        for mission in mission_list:
            self.enqueue(mission.serialize())
        if self.limited:
            self.endpoint = str(uuid.uuid4())
            self.enqueue(self.endpoint)

    def serialize(self):
        pass


class MemQueue(object):
    _CACHE_LIST = []

    def __init__(self, name: str, limited=False):
        self.name = name
        self._queue = Queue()
        self.limited = limited
        self.endpoint = None
        if '%s_queue' % name in os.listdir(os.path.abspath(os.curdir)):
            with open('./%s_queue' % name, 'r')as f:
                mission_list = f.readlines()
                for mission_str in mission_list:
                    mission_str = mission_str.replace('\n', '')
                    self.enqueue(mission_str)
                    MemQueue._CACHE_LIST.append(Mission.deserialize(mission_str))

    @property
    def queue_size(self):
        return self._get_queue_size()

    def _get_queue_size(self):
        return self._queue.qsize()

    def enqueue(self, value: str):
        self._queue.put(value)

    def dequeue(self, timeout=None):
        element = self._queue.get(timeout=timeout)
        return element if element else None

    def init_queue(self, mission_list: list):
        unique_tag_list = [m.unique_tag for m in MemQueue._CACHE_LIST]
        if '%s_queue' % self.name not in os.listdir(os.path.abspath(os.curdir)):
            for mission in mission_list:
                if mission.unique_tag not in unique_tag_list:
                    self.enqueue(mission.serialize())
            if self.limited:
                self.endpoint = str(uuid.uuid4())
                self.enqueue(self.endpoint)

    def serialize(self):
        with open('./%s_queue' % self.name, 'w')as f:
            while 1:
                try:
                    url = self.dequeue(timeout=1)
                    if self.endpoint:
                        if url == self.endpoint:
                            break
                except Empty:
                    break
                else:
                    f.write(str(url))
                    f.write('\n')