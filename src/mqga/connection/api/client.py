from __future__ import annotations

from functools import cached_property
import asyncio
import time
import json
import logging
import sys
from reprlib import Repr

from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from mqga.bot import Bot
    from mqga.q.api import AccessToken
    UseClientDefault = httpx._client.UseClientDefault

from mqga import LEGACY
from mqga.log import log

class APIError(Exception):

    def __init__(self, data: dict):
        self._data = data
        super().__init__(self._data)
        # if message := self.message:
        #     super().__init__(self.code, message)
        # else:
        #     super().__init__(self.code)

    @property
    def code(self):
        return self._data.get("code") or self._data["ret"]

    @property
    def message(self):
        return self._data.get("message") or self._data.get("msg")  # 什么玩意

class APIClient:

    def __init__(self, bot: Bot):
        self.bot = bot

        self._token = ""
        self._expire_time = 0
        self._fetch_time = 0

        self._client: httpx.AsyncClient | None = None

    if LEGACY:
        @property
        def _authorization(self):
            return f"Bot {self.bot.APPID}.{self.bot.APP_TOKEN}"

        @cached_property
        def header(self):
            return {"Authorization": self._authorization}
    else:
        @property
        def _authorization(self):
            return f"QQBot {self._token}"

        @cached_property
        def header(self):
            return {
                "Authorization": self._authorization,
                "X-Union-Appid": f"{self.bot.APPID}"
            }

    @cached_property
    def _token_data(self):
        return {
            "appId": f"{self.bot.APPID}",
            "clientSecret": f"{self.bot.APP_SECRET}",
        }

    @cached_property
    def _token_task(self):
        return asyncio.create_task(self._fetch_token())

    @property
    async def authorization(self):
        """ 需要 await 去检查是否是最新的 """
        await self._ensure_token()
        return self._authorization

    @cached_property
    def _base_url(self):
        return (r"https://api.sgroup.qq.com/", r"https://sandbox.api.sgroup.qq.com")[self.bot.in_sandbox]

    async def _get(self, api: str, params: dict | None = None, timeout: float | UseClientDefault = httpx.USE_CLIENT_DEFAULT, **kw):
        await self._ensure_token()
        assert self._client, "发送请求时 client 应该已存在"
        log_info_http(f"GET {api}", params)
        # log.debug(f"GET {api} {params!r}")
        return self._handle_response(await self._client.get(api, params=params, timeout=timeout, **kw))

    async def _post(self, api: str, json: dict | None = None, timeout: float | UseClientDefault = httpx.USE_CLIENT_DEFAULT, **kw):
        await self._ensure_token()
        assert self._client, "发送请求时 client 应该已存在"
        # log.debug(f"POST {api} {json if json is not None else kw.get('data')!r}")
        log_info_http(f"POST {api}", json if json is not None else kw.get('data'))
        return self._handle_response(await self._client.post(api, json=json, timeout=timeout, **kw))

    async def _put(self, api: str, json: dict | None = None, timeout: float | UseClientDefault = httpx.USE_CLIENT_DEFAULT, **kw):
        await self._ensure_token()
        assert self._client, "发送请求时 client 应该已存在"
        # log.debug(f"PUT {api} {json if json is not None else kw.get('data')!r}")
        log_info_http(f"PUT {api}", json if json is not None else kw.get('data'))
        return self._handle_response(await self._client.put(api, json=json, timeout=timeout, **kw))

    async def _delete(self, api: str, params: dict | None = None, timeout: float | UseClientDefault = httpx.USE_CLIENT_DEFAULT, **kw):
        await self._ensure_token()
        assert self._client, "发送请求时 client 应该已存在"
        # log.debug(f"DELETE {api} {params!r}")
        log_info_http(f"DELETE {api}", params)
        return self._handle_response(await self._client.delete(api, params=params, timeout=timeout, **kw))

    def _handle_response(self, response: httpx.Response):
        http_error = None
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            http_error = e
        if response.status_code == 204 or not response.content: # 无数据
            return True
        try:
            data: dict = response.json()
        except json.JSONDecodeError as e:
            log.error(f"{response.text = !r}")
            if http_error:
                raise http_error # json 解析不出来的情况下，如果有 http_error 就先报出来
            raise e  # json 解析出错
        if (data and ("code" in data or "ret" in data)):
            if http_error:
                raise APIError(data) from http_error
            else:
                raise APIError(data)
        # log.debug(f"{response.status_code} {data or response.is_success !r}")
        result = data or response.is_success
        log_debug_http(response.status_code, result)
        return result

    async def _ensure_token(self):
        if self._token:
            now = time.time()
            if now < self._fetch_time:  # 不用获取新的
                return self._token
            if now < self._expire_time:  # 需要获取新的，但老的也还能用，先把 task 创出来
                self._token_task  # 如果还没有的话，创建
                return self._token
        await self._token_task
        return self._token

    TOKEN_URL = r"https://bots.qq.com/app/getAppAccessToken"
    TOKEN_INTERVAL = 50

    async def _fetch_token(self):
        async with httpx.AsyncClient() as client:
            data: AccessToken = (await client.post(self.TOKEN_URL, json=self._token_data)).json()
        self._token, expire_time = data["access_token"], int(data["expires_in"])
        log.info(f"拿到了新访问符，{expire_time} 秒后要再拿 :(")
        self._expire_time = time.time() + expire_time
        self._fetch_time = self._expire_time - self.TOKEN_INTERVAL  # 过期前就获取新的
        del self.header
        del self._token_task  # 因为要跑完了，删掉自己的 task
        await self._new_client()  # 也换上新的 client
        # return expire_time

    # async def _token_loop(self):
    #     log.info("找企鹅要访问符去了")
    #     self.header = {}  # 一开始没有 token，所以也没有 header
    #     end = self.bot._ended
    #     try:
    #         while not end.is_set():
    #             async with self._new_client():  # 在 token 有效期间保持 client 对象    效果待验证
    #                 await asyncio.sleep(self._sleep_time)

    #                 await self._token_task
    #     finally:
    #         self._token_task.cancel()
    #         log.debug("token loop 结束")

    async def _new_client(self):
        base_url = self._base_url or ""
        timeout = self.bot.TIMEOUT or httpx._config.DEFAULT_TIMEOUT_CONFIG
        old_client = self._client
        self._client = httpx.AsyncClient(
            base_url=base_url, timeout=timeout, headers=self.header)
        if old_client:
            await old_client.aclose()
        return self._client

    async def init(self):
        log.info("API 初始化")
        self.header = {}  # 一开始没有 token，所以也没有 header

    async def stop(self):
        if "_token_task" in self.__dict__:  # 有点丑，用来判断 _token_task 是否存在
            # 用 hasattr 的话，没有任务也会执行一遍创一个出来
            self._token_task.cancel()
        if self._client:
            await self._client.aclose()
        log.info("API 停止")

ShorterRepr = Repr()
ShorterRepr.maxlong = ShorterRepr.maxdict = ShorterRepr.maxlist = sys.maxsize
ShorterRepr.maxstring = 100
# 不限制 dict、list 和总长度
# 但会限制 str 长度
# 目前消息 id 长度为 97，能完整显示

def log_info_http(head, data):
    if not log.isEnabledFor(logging.INFO):
        return
    log.info(f"{head} {ShorterRepr.repr(data)}")

def log_debug_http(head, data):
    if not log.isEnabledFor(logging.DEBUG):
        return
    log.debug(f"{head} {ShorterRepr.repr(data)}")
