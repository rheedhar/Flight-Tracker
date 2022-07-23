import requests


class ApiCall:
    def __init__(self, endpoint, headers, data="null"):
        self.endpoint = endpoint,
        self.data = data,
        self.headers = headers

    def get_requests(self):
        # noinspection PyTypeChecker
        get_response = requests.get(url=self.endpoint, json=self.data, headers=self.headers)
        return get_response.json()

    def get_requests_nd(self):
        # noinspection PyTypeChecker
        get_response = requests.get(url=self.endpoint, headers=self.headers)
        return get_response.json()

    def post_requests(self):
        # noinspection PyTypeChecker
        post_response = requests.get(url=self.endpoint, json=self.data, headers=self.headers)
        return post_response.text

    def put_requests(self):
        # noinspection PyTypeChecker
        put_response = requests.put(url=self.endpoint, json=self.data, headers=self.headers)
        return put_response.text



