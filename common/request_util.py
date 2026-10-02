# -*- coding: utf-8 -*-
"""
接口请求封装：统一 base_url / headers / 日志
"""
import requests
from common.logger import get_logger

logger = get_logger(__name__)


class RequestUtil:
    def __init__(self, base_url: str = "", headers: dict | None = None, timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.timeout = timeout
        if headers:
            self.session.headers.update(headers)

    def request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        kwargs.setdefault("timeout", self.timeout)
        logger.info(f"[{method.upper()}] {url}  params={kwargs.get('params')}  json={kwargs.get('json')}")
        resp = self.session.request(method, url, **kwargs)
        logger.info(f"[{resp.status_code}] {url}  body={resp.text[:500]}")
        return resp

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)