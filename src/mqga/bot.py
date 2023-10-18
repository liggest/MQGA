
from mqga.api import API
from mqga.ws import WS

import asyncio

class Bot:
    """ 统一管理连接、消息处理等，并提供一些方法来调用 api """
    
    def __init__(self):
        self._api = API(self)
        self._ws = WS(self)
        self.APPID = ""
        self.APP_SECRET = ""

    async def init(self):
        self._ended = asyncio.Event()

        assert self.APPID
        assert self.APP_SECRET

        await self._api.init()
        await self._ws.init()

    async def stop(self):
        self._ended.set()
