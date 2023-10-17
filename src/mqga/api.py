
from functools import cached_property
import asyncio


class API:

    def __init__(self, bot):    # TODO
        self.bot = bot
        self._token = ""
        self._expire_time = 0

    @cached_property
    def header(self):
        return {
            "Authorization": f"QQBot {self._token}" if self._token else "",
            "X-Union-Appid": "{BOT_APPID}"         # TODO
        }

    @cached_property
    def token_data(self):
        return {
            "appId": "{BOT_APPID}",                # TODO
            "clientSecret": "{BOT_CLIENTECRET}",   # TODO
        }

    async def get(self, url, params, **kw):        # TODO
        raise NotImplementedError

    async def post(self, url, data, **kw):         # TODO
        raise NotImplementedError

    async def fetch_token(self):
        data = await self.post(r"https://bots.qq.com/app/getAppAccessToken", self.token_data)
        self._token, self._expire_time = data["access_token"], int(data["expires_in"])
        del self.header
        return self._expire_time

    async def token_loop(self):
        print("找腾讯要访问符去了")    # TODO 换成 log
        end = False                 # TODO 真正的 end
        while not end:
            sleep_time = await self.fetch_token()
            sleep_time -= 50  # 过期前就获取新的
            await asyncio.sleep(sleep_time)

    async def init(self):
        asyncio.create_task(self.token_loop())

