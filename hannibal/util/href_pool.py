from redis import Redis
import os


class RedisHrefPool(object):
    def __init__(self, name: str, host: str, pwd: str, port=6379, db=0):
        self.name = name
        self.address = '%s:%d' % (host, port)
        self._pool = Redis(host=host, port=port, db=db, password=pwd)

    @property
    def all_href(self):
        return self._get_all_href()

    def _get_all_href(self):
        return self._pool.smembers(self.name)

    def insert(self, href: str):
        if not self.is_duplicate(href):
            self._pool.sadd(self.name, href)

    def multi_insert(self, href_list: list):
        try:
            for href in href_list:
                self.insert(href)
        except Exception as e:
            print(e)
            return

    def is_duplicate(self, href) -> bool:
        return self._pool.sismember(self.name, href)

    def serialize(self):
        pass


class MemPool(object):
    def __init__(self, name: str):
        self.name = name
        self._pool = list()
        if '%s_pool' % name in os.listdir(os.path.abspath(os.curdir)):
            with open('./%s_pool' % name, 'r')as f:
                url_list = f.readlines()
                for url in url_list:
                    url = url.replace('\n', '')
                    self.insert(url)

    @property
    def all_href(self):
        return self._get_all_href()

    def _get_all_href(self):
        return self._pool

    def insert(self, href: str):
        if not self.is_duplicate(href):
            self._pool.append(href)

    def multi_insert(self, href_list: list):
        try:
            for href in href_list:
                self.insert(href)
        except Exception as e:
            print(e)
            return

    def is_duplicate(self, href) -> bool:
        return href in self._pool

    def serialize(self):
        with open('./%s_pool' % self.name, 'w')as f:
            for url in self.all_href:
                f.write(url)
                f.write('\n')