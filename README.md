# hannibal

A light-weighted, distributed crawler implemented based on asyncio, aiohttp and redis.

For commemorating genneral Hannibal Barca.

### Collecting

Two application design modes supported:

1. Single node contains both collecting and parsing functionality.
2. Distribute structure contains lots of collecting nodes and parsing nodes, interacts with reds-based queue and URL pool.

Two collecting modes supported:

1. Collecting for a list of task.
2. Increasing collection.

### Parsing

Only basic parsing schedule is implemented in parser module, you need to overide the Parser class and implemented the page parsing function by yourself.  Multiple parser modules are supported, beautiful soup, pyquery or regular expression are available.

### Queue and Pool

Both of the two brokers mentioned above are implemented in memory based mode and redis based mode. For memory based queue and pool, basic storage mechanism also implemented.

### Quick Start

##### Installation

```shell
pip install hannibal
```

As mentioned above, in this project 2 collecting modes are implemented in module **LocalCollector** and **DistributeCollector**.

**LocalCollector** requires a **mission queue** for passing packed collecting missions, a **href pool** for avoiding duplicate collecting, and a **parser function** for parsing collecting result. For **DistributeCollector**, the requirement is basically the same as **DistributeCollector**'s, except it requires a **parse queue** for passing the collecting result to another parser node.

##### Simple Usage

```python
from hannibal.spider import LocalCollector, MemPool, MemQueue, extract_json, Mission

pool = MemPool(name='http_bin')
queue = MemQueue(name='http_bin', limited=True)
url_list = [Mission(unique_tag=i, url='http://httpbin.org/get?t=%d' % i) for i in range(1, 500)]
queue.init_queue(url_list)
collector = LocalCollector(mission_queue=queue, href_pool=pool, parse_function=collect_function, cache_size=10)
collector.conquer()
```

