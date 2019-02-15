from random import choice
from threading import Thread


class TrickHelper(object):
    HEADERS = [
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
        'IE 9.0User-Agent:Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
        'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER) ',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36'
    ]

    def __init__(self, pool_size=100, use_https=False, use_proxy=False, proxy_provider=None, referer=None):
        self.use_proxy = use_proxy
        self._proxy_pool = None
        self.use_https = use_https
        self.proxy_prefix = 'https://' if self.use_https else 'http://'
        self.lock = False
        self.pool_size = pool_size
        self.threshold = int(pool_size / 2)
        self.proxy_provider = proxy_provider
        if self.use_proxy and not proxy_provider:
            raise AttributeError(
                "Proxy provider must be configured if you would like to use proxy server for request redirection.")
        elif self.use_proxy:
            self._proxy_pool = []
            self.register_proxy_provider(proxy_provider)
            self.update_pool()
        self.referer = referer
        self.header = dict()

    def register_proxy_provider(self, proxy_provider):
        if not hasattr(proxy_provider, '__call__'):
            raise AttributeError('Given Provider is not callable')
        else:
            self.proxy_provider = proxy_provider

    def trick(self):
        agent = self.get_random_agent()
        self.header['User-Agent'] = agent
        if self.referer:
            self.header['Referer'] = self.referer
        return self.header

    def customize_header(self, header_dict):
        for k, v in header_dict.items():
            self.header[k] = v

    @staticmethod
    def get_random_agent():
        return choice(TrickHelper.HEADERS)

    def get_proxy(self):
        if not self.use_proxy:
            return None
        else:
            try:
                proxy_ip = choice(self._proxy_pool)
            except Exception as e:
                print(e)
                return None
            else:
                http_request_proxy = self.proxy_prefix + proxy_ip
                if len(self._proxy_pool) <= self.threshold:
                    Thread(target=self.update_pool()).start()
                return http_request_proxy

    def update_pool(self):
        if not self.proxy_provider:
            raise NotImplementedError("Proxy provider function needed to be implemented.")
        elif not self.lock:
            self.lock = True
            proxy_list = self.proxy_provider()
            for proxy in proxy_list:
                self._proxy_pool.append(proxy)


if __name__ == '__main__':
    t = TrickHelper()
    print(t.trick())
