import abc
import logging

import requests


logger = logging.getLogger(__name__)


class URLShortifier(abc.ABC):
    URL = None

    def __init__(self, access_token: str):
        self._access_token = access_token

    @abc.abstractmethod
    def get_short_link(self, link: str) -> str:
        pass

    def _send_request(self, payload: dict, **kwargs: dict) -> dict:
        logger.info(
            f"Sending request to Shorifier API: {self.URL} - {payload} - {kwargs}"
        )
        try:
            r = requests.post(self.URL, json=payload, **kwargs)
            r.raise_for_status()
            return r.json()
        except Exception as ex:
            logger.exception(f"Failed to send a request: {str(ex)}", exc_info=True)
            return None


class BitlyShortifier(URLShortifier):
    URL = "https://api-ssl.bitly.com/v3/shorten"

    def get_short_link(self, link: str) -> str:
        params = {
            'access_token': self._access_token,
            "format": "json",
            "longUrl": link,
        }

        return super()._send_request({}, params=params) ["data"]["url"] or link


class GooglShortifier(URLShortifier):
    URL = "https://www.googleapis.com/urlshortener/v1/url"

    def get_short_link(self, link: str) -> str:
        payload = {
            "longUrl": link,
        }
        params = {
            "at": self._access_token,
        }

        return super()._send_request(payload, params=params)["id"] or link
