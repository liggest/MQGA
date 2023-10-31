from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot

from functools import cached_property
import asyncio

import websockets

from mqga.log import log
from mqga.q.constant import WSState, DefaultIntents
from mqga.q.payload import Payload
from mqga.q.payload import HelloPayload, HeartbeatPayload, HeartbeatAckPayload, InvalidSessionPayload, ReconnectPayload
from mqga.q.payload import ResumePayload, ResumeData, IdentifyPayload, IdentifyData
from mqga.q.payload import EventPayload, ReadyEventPayload, ResumedEventPayload, ChannelAtMessageEventPayload
from mqga.q.payload import receive_payloads_type

class WS:

    def __init__(self, bot:Bot):
        self.bot = bot
        self.url = ""
        self.client = None
        self._connect_task: asyncio.Task = None
        self.state = WSState.Closed

        self.intents = DefaultIntents
        self._heartbeat_interval = 0
        self._session_id = ""
        self._last_seq_no = 0

        self._heartbeat_task: asyncio.Task = None

    @cached_property
    def ReceivePayloadsType(self):
        return receive_payloads_type()

    async def init(self):
        log.info("WS 初始化")
        self._connect_task = asyncio.create_task(self.connect())
        self._connect_task.add_done_callback(self._task_done)

    async def stop(self):
        log.info("WS 停止")
        if self._connect_task:
            self._connect_task.cancel()
        if "ReceivePayloadsType" in self.__dict__:
            del self.ReceivePayloadsType

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
            self.state = WSState.Connecting
            async with websockets.connect(self.url) as self.client:
                log.info("WS 已连接")
                self.state = WSState.ConnectedRaw
                await self.receive()
        except websockets.exceptions.ConnectionClosed:
            log.warning("WS 连接关闭")
        finally:
            log.info("WS 已断开")
            self.state = WSState.Closed
            if not self.bot._ended.is_set():
                await self.reconnect()

    async def reconnect(self, delay=3.0):
        log.info(f"WS {delay} 秒后尝试重连")
        await asyncio.sleep(delay)
        self._connect_task = asyncio.create_task(self.connect())
        self._connect_task.add_done_callback(self._task_done)

    def _task_done(self, task: asyncio.Task):
        if task.cancelled():
            log.warning(f"WS 任务 {task} 取消")
        elif e := task.exception():
            log.exception(f"WS 任务 {task} 失败", exc_info=e)
                

    async def receive(self):
        client = self.client
        end = self.bot._ended
        while not end.is_set():
            asyncio.create_task(self.handle(await client.recv()))

    async def handle(self, data: websockets.Data):
        from pydantic import ValidationError
        try:
            payload = self.ReceivePayloadsType.validate_json(data)
            log.debug(f"{type(payload)!r} {payload.model_dump()}")
        except ValidationError as e:
            payload = None
            log.exception(f"raw: {data!r}, error:{e.json(include_url=False)!r}", exc_info=e)
        match payload:
            case HelloPayload():
                self._heartbeat_interval = payload.data.heartbeat_interval / 1000
                token = self.bot._api.header["Authorization"]
                if self._session_id:
                    await self._send_payload(ResumePayload(data=ResumeData(token=token, session_id=self._session_id, seq=self._last_seq_no)))
                else:
                    await self._send_payload(IdentifyPayload(data=IdentifyData(token=token, intents=self.intents)))
            case EventPayload():
                self._last_seq_no = payload.seq_no
                log.debug(f"收到事件：{payload.type}")
                match payload:
                    case ReadyEventPayload():
                        self._session_id = payload.data.session_id
                        log.debug(f"我的信息：{payload.data.user!r}")
                        self._start_heartbeat()
                        self.state = WSState.ConnectedSession
                    case ResumedEventPayload():
                        self._start_heartbeat()
                        self.state = WSState.ConnectedSession
                    case ChannelAtMessageEventPayload():
                        log.debug(f"收到消息：{payload.data!r}")
                        if payload.data.content.lower().endswith("hello"):
                            await self.bot._api.channel_reply("全体目光向我看齐，我宣布个事儿！\nMQGA！", payload)
            case InvalidSessionPayload():
                self._session_id = ""
            case HeartbeatAckPayload() | ReconnectPayload():
                pass

    async def _send_payload(self, payload: Payload):
        log.debug(payload.model_dump(by_alias=True))
        await self.client.send(payload.model_dump_json(by_alias=True))

    def _start_heartbeat(self):
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._heartbeat_task.add_done_callback(self._task_done)

    async def _heartbeat_loop(self):
        log.info("心砰砰地跳")
        while self.client.open:
            await self._send_payload(HeartbeatPayload(data=self._last_seq_no or None))
            await asyncio.sleep(self._heartbeat_interval)
