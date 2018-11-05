from hannibal.spider import LocalCollector
from hannibal.util import MemPool, MemQueue, extract_json, Mission, RedisQueue

pool = MemPool(name='investment')
queue = MemQueue(name='investment', limited=True)
storage_queue = RedisQueue(host='your_host', pwd='your_pwd', name='projects', db=12)


async def collect_function(response):
    json_obj = await extract_json(response)
    print(json_obj)
    for item in json_obj['data']['projectlist']:
        storage_queue.enqueue(
            Mission(unique_tag=item['projectid'], url='https://www.xytzq.cn:9443/tzq/pc/project/getProjectInfo',
                    method='POST',
                    data={'projectid': item['projectid']}).serialize())


def get_project_id():
    url_list = [Mission(unique_tag=i, url='https://www.xytzq.cn:9443/tzq/pc/project/getAllProjectList', method='POST',
                        data={'page': i, 'tradeid': 0, 'processid': 0}) for i in range(1, 5)]
    queue.init_queue(url_list)
    collector = LocalCollector(collect_queue=queue, href_pool=pool, parse_function=collect_function, cache_size=3,
                               data_type='data')
    collector.conquer()


if __name__ == '__main__':
    get_project_id()