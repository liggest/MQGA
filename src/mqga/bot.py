
import asyncio

from mqga import LEGACY
from mqga.connection.api import API
from mqga.connection.ws import WS
from mqga.log import log


class Bot:
    """ 统一管理连接、消息处理等，并提供一些方法来调用 api """
    
    def __init__(self):
        from mqga.toml import config  # 暂时放在这里，让它在 bot 初始化的时候再加载
        self.config = config

        self._api = API(self)
        self._ws = WS(self)


    @property
    def APPID(self):
        return self.config.AppID

    @property
    def APP_SECRET(self):
        return self.config.Secret

    if LEGACY:
        @property
        def APP_TOKEN(self):
            return self.config.Token

    @property
    def BASE_URL(self):
        # raise NotImplementedError
        return r"https://sandbox.api.sgroup.qq.com"
    
    @property
    def TIMEOUT(self):
        # raise NotImplementedError
        return None

    async def init(self):
        log.info("Bot 初始化，MQGA！")
        self._ended = asyncio.Event()

        await self._api.init()
        await self._ws.init()

    async def stop(self):
        self._ended.set()
        log.info("Bot 准备停止…")

    async def _run(self):
        async with self._api, self._ws, self:
            await self.init()
            await self._ended.wait()

    async def __aenter__(self):
        # 并不在这里初始化，而是在 bot 初始化时初始化
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    def run(self):
        """ 入口 """  # TODO 暂定
        asyncio.run(self._run())
