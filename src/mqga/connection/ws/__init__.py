""" Websocket 连接 """

from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot

import asyncio

import websockets

from mqga.log import log
from mqga.connection.ws.inner import WSInner

class WS:

    def __init__(self, bot:Bot):
        self.bot = bot
        self.url = ""
        self.client = None
        self._connect_task: asyncio.Task = None

        self.inner: WSInner = None

    async def init(self):
        log.info("WS 初始化")
        self.inner = WSInner(self)
        self._start_connect()

    async def stop(self):
        log.info("WS 停止")
        if self._connect_task:
            self._connect_task.cancel()
        self.inner.to_closed()
        self.inner = None

    async def __aenter__(self):
        # 并不在这里初始化，而是在 bot 初始化时初始化
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def connect(self):
        if not self.url:
            log.info("WS 正在获取接入点")
            self.url = await self.bot._api.ws_url()
            log.debug(f"WS 拿到接入点 {self.url}")
        
        try:
            self.inner.to_connecting()
            async with websockets.connect(self.url) as self.client:
                log.info("WS 已连接")
                self.inner.to_connected_raw()
                await self.receive()
        except websockets.exceptions.ConnectionClosed:
            log.warning("WS 连接关闭")
        finally:
            log.info("WS 已断开")
            if self.inner:
                self.inner.to_closed()
            if not self.bot._ended.is_set():
                await self.reconnect()

    async def reconnect(self, delay=3.0):
        log.info(f"WS {delay} 秒后尝试重连")
        await asyncio.sleep(delay)
        self._start_connect()

    async def receive(self):
        client = self.client
        end = self.bot._ended
        while not end.is_set():
            asyncio.create_task(self.inner(await client.recv()))
                
    def _task_done(self, task: asyncio.Task):
        if task.cancelled():
            log.warning(f"WS 任务 {task} 取消")
        elif e := task.exception():
            log.exception(f"WS 任务 {task} 失败", exc_info=e)

    def _start_connect(self):
        self._connect_task = asyncio.create_task(self.connect())
        self._connect_task.add_done_callback(self._task_done)
