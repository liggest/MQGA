
from mqga.api import API
from mqga.ws import WS
from mqga.args import *
from mqga.log import log

import asyncio

class Bot:
    """ 统一管理连接、消息处理等，并提供一些方法来调用 api """
    
    def __init__(self):

        self._api = API(self)
        self._ws = WS(self)

        from mqga.toml import config  # 暂时放在这里，让它在 bot 初始化的时候再加载
        self.config = config

    @property
    def APPID(self):
        return self.config.AppID

    @property
    def APP_SECRET(self):
        return self.config.Secret

    @property
    def BASE_URL(self):
        raise NotImplementedError  # TODO
    
    @property
    def TIMEOUT(self):
        raise NotImplementedError  # TODO

    async def init(self):
        log.info("Bot 初始化，MQGA！")
        self._ended = asyncio.Event()

        assert self.APPID
        assert self.APP_SECRET

        await self._api.init()
        await self._ws.init()

    async def stop(self):
        self._ended.set()
        log.info("Bot 准备停止…")

    def run(self):
        """ 入口 """  # TODO 暂定
        asyncio.run(self.init())
