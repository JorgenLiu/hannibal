import json


class Mission(object):
    def __init__(self, unique_tag, url, method='GET', data=None, data_type='data'):
        self.unique_tag = str(unique_tag)
        self.url = url
        if method not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise ValueError('invalid method')
        else:
            self.method = method
        self.data = data
        if data_type not in ['json', 'data']:
            raise ValueError('invalid data type')
        else:
            self.data_type = data_type

    def serialize(self):
        return json.dumps(self.__dict__)

    @classmethod
    def deserialize(cls, str_obj):
        try:
            assert isinstance(str_obj, str)
            mission_dict = json.loads(str_obj)
            assert isinstance(mission_dict, dict)
        except AssertionError:
            return None
        else:
            mission = cls(
                unique_tag=mission_dict.get('unique_tag'),
                url=mission_dict.get('url'),
                method=mission_dict.get('method'),
                data=mission_dict.get('data'),
                data_type=mission_dict.get('data_type')
            )
            return mission


async def extract_html(response, encoding='utf-8'):
    return await response.text(encoding=encoding)


async def extract_json(response, encoding='utf-8'):
    return await response.json(encoding=encoding)
