import time
from datetime import datetime, timedelta
from random import randint
from urllib.parse import unquote, urljoin

import adal
import requests
from logzero import setup_logger

import settings

MAX_ATTEMPTS = 5


class ThrottlingException(Exception):
    def __init__(self, wait_sec):
        self.wait_sec = wait_sec


class TooManyThrottlingException(Exception):
    def __init__(self, message):
        self.message = message


def retry_on_throttling(req):
    """ Decorator for requests which may raise ThrottlingException.
        When a request raises ThrottlingException, the request will be retried unless exceeding MAX_ATTEMPTS.
    """
    def wrapper(*args, **kwargs):
        for _ in range(MAX_ATTEMPTS):
            try:
                return req(*args, **kwargs)
            except ThrottlingException as e:
                time.sleep(e.wait_sec)
                continue

        raise TooManyThrottlingException(
            'Exceeded maximum number of attempts.')

    return wrapper


class GraphClient():
    def __init__(self, tenant_name, client_id, client_secret, chasing_enable=True, logging_enable=False):
        # settings of logging
        self.logger = setup_logger()
        self.logger.disabled = not logging_enable

        # settings of adal and ms graph
        self.graph_base_url = 'https://graph.microsoft.com/'
        self.graph_version = 'beta'  # or 'v1.0'
        self.authority_url = f'https://login.microsoftonline.com/{tenant_name}'
        self.client_id = client_id
        self.client_secret = client_secret
        
        # chase next links
        self.chasing_enable = chasing_enable
        
        # refresh token 10 minutes before expiration
        self.time_to_refresh_token_sec = 600
        self.context = adal.AuthenticationContext(self.authority_url)
        self.token = self._get_token()

        # settings of retrying
        self.retry_enabled = True
        self.wait_random_min = 3
        self.wait_random_max = 5

    def _get_token(self):
        return self.context.acquire_token_with_client_credentials(
            self.graph_base_url, self.client_id, self.client_secret)

    def _token_expires_on(self):
        token_time_format = '%Y-%m-%d %H:%M:%S.%f'
        return datetime.strptime(self.token['expiresOn'], token_time_format)

    def _is_token_old(self):
        expires_in = self._token_expires_on() - datetime.now()
        return expires_in < timedelta(seconds=self.time_to_refresh_token_sec)

    def _refresh_token_if_needed(self):
        if self._is_token_old():
            self.token = self._get_token()

    def _get_chasing(self, api_path, params=None):
        """ get all data, chasing next links
        """
        res = self._request('GET', api_path, params=params).json()
        values = res['value']
        next_url = res['@odata.nextLink'] if '@odata.nextLink' in res else None
        while next_url:
            res = self._request('GET', next_url).json()
            values += res['value']
            next_url = res['@odata.nextLink'] if '@odata.nextLink' in res else None

        return values

    @retry_on_throttling
    def _request(self, method, api_path, params=None, data=None):
        self._refresh_token_if_needed()

        if api_path.startswith(self.graph_base_url):
            url = api_path
        else:
            url = urljoin(self.graph_base_url,
                          '/'.join([self.graph_version] + api_path.split('/')))
        headers = {'Authorization':  self.token['accessToken'],
                   'Content-Type': 'application/json'}
        res = requests.request(method, url, params=params, json=data,
                               headers=headers, stream=False)

        if res.ok:
            self.logger.info(
                f'{res.request.method} {res.status_code} {unquote(res.request.url)}')
        elif res.status_code == 429 and self.retry_enabled:
            self.logger.warn(
                f'{res.request.method} {res.status_code} {unquote(res.request.url)}')
            if 'Retry-After' in res.headers:
                wait_sec = int(res.headers['Retry-After'])
            else:
                wait_sec = randint(self.wait_random_min, self.wait_random_max)

            self.logger.warn(
                f'{res.request.method} {res.status_code} {unquote(res.request.url)}' +
                f'\nThe request will be retried in {wait_sec} secs')
            raise ThrottlingException(wait_sec)
        else:
            self.logger.error(
                f'{res.request.method} {res.status_code} {unquote(res.request.url)}\n{res.headers}\n{res.text}')
            res.raise_for_status()

        return res

    def get(self, api_path, params=None):
        if self.chasing_enable:
            return self._get_chasing(api_path, params=params)
        else:
            return self._request('GET', api_path, params=params)

    def post(self, api_path, params=None, data=None):
        return self._request('POST', api_path, params=params, data=data)

    def patch(self, api_path, params=None, data=None):
        return self._request('PATCH', api_path, params=params, data=data)

    def put(self, api_path, params=None, data=None):
        return self._request('PUT', api_path, params=params, data=data)

    def delete(self, api_path, params=None, data=None):
        return self._request('DELETE', api_path, params=params, data=data)
