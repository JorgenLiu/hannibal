from hannibal.spider import LocalCollector
from hannibal.util import MemPool, extract_json, RedisQueue

pool = MemPool(name='projects')
queue = RedisQueue(host='your_host', pwd='your_pwd', name='projects', db=12)
storage_queue = RedisQueue(host='your_host', pwd='your_pwd', name='project_info', db=13)


async def collect_function(response):
    json_obj = await extract_json(response)
    print(json_obj)
    storage_queue.enqueue(str(json_obj))


def get_project_info():
    collector = LocalCollector(collect_queue=queue, href_pool=pool, parse_function=collect_function, cache_size=3,
                               data_type='data')
    collector.conquer()


if __name__ == '__main__':
    get_project_info()