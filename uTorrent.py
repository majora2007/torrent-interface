''' 
    @name uTorrent.py
    @author Joseph Milazzo
    @description Simple connector to uTorrent Web API. 
'''
import requests

class uTorrent:
    _session = None
    _response = None
    _token = ""
    _base_url = ""

    def __init__(self, base_url, username, password):
        self._session = requests.Session()
        self._session.auth = (username, password)

        self._base_url = base_url
        self._fetch_token()

    def _fetch_token(self):
        """Fetch token from Web API."""

        url = self._base_url + 'token.html'
        self._response = self._session.get(url)

        if self._response.status_code != 200:
            return

        from BeautifulSoup import BeautifulSoup
        html = self._response.text
        parsed_html = BeautifulSoup(html)
        self._token = parsed_html.find('div', attrs={'id':'token'}).text

    def _make_request(self, params):
        try:
            resp = self._session.get(self._base_url, params=params)
        except requests.exceptions.ConnectionError,e:
            raise e

        if resp.status_code == 400:
            pass
        elif resp.status_code != 200:
            self._fetch_token()

    def _make_params(self, token, action, hash):
        return {'token': token, 'action': action, 'hash': hash}

    def start_torrent(self, hash):
        url = self._base_url
        self._session.get(url, params=self._make_params(self._token, 'start', hash))

    def stop_torrent(self, hash):
        self._session.get(self._base_url, params=self._make_params(self._token, 'stop', hash))

    def pause_torrent(self, hash):
        self._session.get(self._base_url, params=self._make_params(self._token, 'pause', hash))

    def unpause_torrent(self, hash):
        self._session.get(self._base_url, params=self._make_params(self._token, 'unpause', hash))

    def forcestart_torrent(self, hash):
        self._session.get(self._base_url, params=self._make_params(self._token, 'forcestart', hash))

    def recheck_torrent(self, hash):
        self._session.get(self._base_url, params=self._make_params(self._token, 'recheck', hash))

    def remove_torrent(self, hash):
        self._session.get(self._base_url, params=self._make_params(self._token, 'remove', hash))

    def remove_data_torrent(self, hash):
        self._session.get(self._base_url, params=self._make_params(self._token, 'removedata', hash))





