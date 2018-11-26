from hannibal.spider import LocalCollector
from hannibal.util import MemPool, MemQueue, extract_json, Mission

pool = MemPool(name='http_bin')
queue = MemQueue(name='http_bin', limited=True)


async def collect_function(response):
    json_obj = await extract_json(response)
    print(json_obj)


def demo_handler(response, url):
    print('handel 400')


def demo_before_collect_middleware(mission):
    print('this is url: %s' % mission.url)


def demo_before_collect_middleware1(mission):
    print('this is tag: %s' % mission.unique_tag)


def ping_http_bin():
    url_list = [Mission(unique_tag=i, url='http://httpbin.org/get?t=%d' % i) for i in range(1, 500)]
    queue.init_queue(url_list)
    collector = LocalCollector(mission_queue=queue, href_pool=pool, parse_function=collect_function, cache_size=10)
    collector.register_middleware(demo_before_collect_middleware)
    collector.register_middleware(demo_before_collect_middleware1)
    collector.register_error_handler(400, demo_handler)
    collector.conquer()


if __name__ == '__main__':
    ping_http_bin()