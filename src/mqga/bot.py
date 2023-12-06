
from contextlib import asynccontextmanager
import asyncio

from mqga import LEGACY
from mqga.connection.api import API
from mqga.connection.ws import WS
from mqga.log import log
from mqga.event.manager import Manager as EventManager
from mqga.lookup.context import BotContext
from mqga.plugin import loader

class Bot:
    """ 统一管理连接、消息处理等，并提供一些方法来调用 api """
    
    def __init__(self):
        from mqga.toml import config  # 暂时放在这里，让它在 bot 初始化的时候再加载
        self.config = config

        self._api = API(self)
        self._ws = WS(self)
        self._em = EventManager(self)


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
    def in_sandbox(self):
        return self.config.Sandbox
    
    @property
    def is_public(self):
        return self.config.Public

    @property
    def TIMEOUT(self):
        # raise NotImplementedError  # TODO
        return None
    
    # @property
    # def PLUGIN_PATH(self):
    #     from pathlib import Path
    #     return Path("./mqga_plugin/mqga_plugin")

    @property
    def intents(self):
        return self._em.intents

    async def init(self):
        log.info("Bot 初始化，MQGA！")

        self._context = BotContext(self)
        self._plugins = loader.load()
        
        await self._api.init()
        await self._ws.init()

    async def stop(self):
        self._ended.set()
        log.info("Bot 准备停止…")

    @asynccontextmanager
    async def _stopper(self):
        self._ended = asyncio.Event()
        try:
            yield
        finally:
            await self.stop()

    async def _run(self):
        async with (self, 
                    self._api, 
                    self._ws, 
                    self._stopper()
                    ):
            # asyncio.create_task(self.subprocess_debug())
            await self.init()
            await self._ended.wait()

    async def __aenter__(self):
        # 并不在这里初始化，而是在 bot 初始化时初始化
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is asyncio.CancelledError:
            log.info("Bot 取消执行")

    # async def subprocess_debug(self):
    #     import os
    #     while True:
    #         print("self", id(self), os.getpid())
    #         await asyncio.sleep(10)

    def run(self):
        """ 入口 """  # 暂定
        try:
            asyncio.run(self._run())
        except KeyboardInterrupt:
            log.info("Bot 已成功打断")

    @property
    def user(self):
        """ bot 用户信息 """
        if self._ws.inner:
            return self._ws.inner._user

    @property
    def api(self):
        """ 官方提供的各种功能 """
        return self._api
