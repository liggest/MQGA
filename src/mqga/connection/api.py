from __future__ import annotations

from functools import cached_property
import asyncio
import time

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
        self._fetch_time = 0

        self._client: httpx.AsyncClient = None

    @cached_property
    def header(self):
        return {
            "Authorization": f"QQBot {self._token}",
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
    async def token(self):
        await self._ensure_token()
        return self._token

    @cached_property
    def _base_url(self):
        return self.bot.BASE_URL

    async def get(self, api:str, params:dict=None, timeout:float=httpx.USE_CLIENT_DEFAULT, **kw):
        await self._ensure_token()
        return (await self._client.get(api, params=params, timeout=timeout, **kw)).json()

    async def post(self, api:str, data:dict, timeout:float=httpx.USE_CLIENT_DEFAULT, **kw):
        await self._ensure_token()
        return (await self._client.post(api, json=data, timeout=timeout, **kw)).json()

    async def _ensure_token(self):
        if self._token:
            now = time.time()
            if now < self._fetch_time: # 不用获取新的
                return self._token
            if now < self._expire_time: # 需要获取新的，但老的也还能用，先把 task 创出来
                self._token_task  # 如果还没有的话，创建
                return self._token
        await self._token_task
        return self._token
        
    TOKEN_URL = r"https://bots.qq.com/app/getAppAccessToken"
    TOKEN_INTERVAL = 50

    async def _fetch_token(self):
        async with httpx.AsyncClient() as client:
            data = (await client.post(self.TOKEN_URL, json=self._token_data)).json()
        self._token, expire_time = data["access_token"], int(data["expires_in"])
        log.info(f"拿到了新访问符，{expire_time} 秒后要再拿 :(")
        self._expire_time = time.time() + expire_time
        self._fetch_time= self._expire_time - self.TOKEN_INTERVAL  # 过期前就获取新的
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
    #             async with self._new_client():  # 在 token 有效期间保持 client 对象  TODO: 效果待验证
    #                 await asyncio.sleep(self._sleep_time)
                    
    #                 await self._token_task
    #     finally:
    #         self._token_task.cancel()
    #         log.debug("token loop 结束")
    
    async def _new_client(self):
        base_url = self._base_url or ""
        timeout = self.bot.TIMEOUT or httpx._config.DEFAULT_TIMEOUT_CONFIG
        old_client = self._client
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout, headers=self.header)
        if old_client:
            await old_client.aclose()
        return self._client
    
    async def init(self):
        log.info("API 初始化")

    async def exit(self):
        if "_token_task" in self.__dict__:  # 有点丑，用来判断 _token_task 是否存在
            # 用 hasattr 的话，没有任务也会执行一遍创一个出来
            self._token_task.cancel()
        if self._client:
            await self._client.aclose()
        log.info("API 退出")

    async def __aenter__(self):
        await self.init()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.exit()
