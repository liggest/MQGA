from __future__ import annotations

from functools import cached_property
import asyncio

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot

from mqga.log import log

class API:

    def __init__(self, bot: Bot):
        self.bot = bot
        self._token = ""
        self._expire_time = 0

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

    async def get(self, url, params, **kw):        # TODO
        raise NotImplementedError

    async def post(self, url, data, **kw):         # TODO
        raise NotImplementedError

    async def _fetch_token(self):
        data = await self.post(r"https://bots.qq.com/app/getAppAccessToken", self._token_data)
        self._token, self._expire_time = data["access_token"], int(data["expires_in"])
        del self.header
        log.info(f"拿到了新访问符，{self._expire_time} 秒后要再拿 :(")
        return self._expire_time

    async def _token_loop(self):
        log.info("找腾讯要访问符去了")
        self.header = {}  # 一开始没有 token，所以也没有 header
        end = self.bot._ended
        while not end.is_set():
            sleep_time = await self._fetch_token()
            sleep_time -= 50  # 过期前就获取新的
            await asyncio.sleep(sleep_time)

    async def init(self):
        log.info(f"API 初始化")
        asyncio.create_task(self._token_loop())

