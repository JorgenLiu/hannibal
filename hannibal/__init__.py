__version__ = '0.0.8'

from hannibal.parser.parser import IncreasingParser, BaseParser
from hannibal.spider.distribute_collector import DistributeCollector
from hannibal.spider.local_collector import LocalCollector
from hannibal.util.queues import RedisQueue, MemQueue
from hannibal.util.tricks import TrickHelper
from hannibal.util.href_pool import RedisHrefPool, MemPool
from hannibal.util.common_utils import Mission, extract_html, extract_json
