from __future__ import annotations

from functools import cached_property
from contextlib import asynccontextmanager
import asyncio

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot

import httpx

from mqga.log import log

class API:

    def __init__(self, bot: Bot):
        self.bot = bot
        self._token = ""
        self._expire_time = 0
        self._client: httpx.AsyncClient = None

    @cached_property
    def header(self):
        return {
            "Authorization": f"QQBot {self._token}" if self._token else "",
            "X-Union-Appid": f"{self.bot.APPID}"
        }

    @cached_property
    def _token_data(self):
        return {
            "appId": f"{self.bot.APPID}",
            "clientSecret": f"{self.bot.APP_SECRET}",
        }

    @cached_property
    def _base_url(self):
        return self.bot.BASE_URL

    async def get(self, api:str, params:dict=None, timeout:float=httpx.USE_CLIENT_DEFAULT, **kw):
        return (await self._client.get(api, params=params, timeout=timeout, **kw)).json()

    async def post(self, api:str, data:dict, timeout:float=httpx.USE_CLIENT_DEFAULT, **kw):
        return (await self._client.post(api, json=data, timeout=timeout, **kw)).json()

    TOKEN_URL = r"https://bots.qq.com/app/getAppAccessToken"

    async def _fetch_token(self):
        async with httpx.AsyncClient() as client:
            data = (await client.post(self.TOKEN_URL, json=self._token_data)).json()
        self._token, self._expire_time = data["access_token"], int(data["expires_in"])
        del self.header
        log.info(f"拿到了新访问符，{self._expire_time} 秒后要再拿 :(")
        return self._expire_time

    async def _token_loop(self):
        log.info("找企鹅要访问符去了")
        self.header = {}  # 一开始没有 token，所以也没有 header
        end = self.bot._ended
        sleep_time = 0
        try:
            while not end.is_set():
                async with self._new_client():  # 在 token 有效期间保持 client 对象  TODO: 效果待验证
                    await asyncio.sleep(sleep_time)
                    sleep_time = await self._fetch_token()
                    sleep_time -= 50  # 过期前就获取新的
        finally:
            log.debug("token loop 结束")
            
    @asynccontextmanager
    async def _new_client(self):
        base_url = self._base_url or ""
        timeout = self.bot.TIMEOUT or httpx._config.DEFAULT_TIMEOUT_CONFIG
        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=timeout, headers=self.header) as client:
                self._client = client
                yield client
        finally:
            self._client = None
    
    async def init(self):
        log.info(f"API 初始化")
        asyncio.create_task(self._token_loop())

