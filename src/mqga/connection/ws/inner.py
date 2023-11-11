from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.connection.ws import WS
    import websockets

import asyncio
from enum import Enum, auto
from functools import cached_property

from pydantic import ValidationError

from mqga.q.payload import Payload
from mqga.q.payload import HeartbeatPayload
from mqga.q.payload import HelloPayload, HeartbeatAckPayload, InvalidSessionPayload, ReconnectPayload
from mqga.q.payload import ResumePayload, ResumeData, IdentifyPayload, IdentifyData
from mqga.q.payload import EventPayload, ReadyEventPayload, ResumedEventPayload
from mqga.q.payload import ChannelAtMessageEventPayload
from mqga.q.payload import ChannelMessageReactionAddEventPayload, ChannelMessageReactionRemoveEventPayload
from mqga.q.payload import receive_payloads_type
from mqga.q.message import User
from mqga.q.constant import Intents
from mqga.log import log

class WSState(Enum):
    """ 连接状态 """
    Closed = auto()
    """ 未连接 """
    Connecting = auto()
    """ 正在连接 """
    ConnectedRaw = auto()
    """ 仅已连接 """
    ConnectedSession = auto()
    """ 已链接，已鉴权 """

class WSInner:
    """ 处理 WS 中各种琐碎的逻辑 """
    
    def __init__(self, ws: WS):
        self.ws = ws
        self._last_seq_no = 0
        self.intents = Intents.DEFAULT | Intents.GUILD_MESSAGE_REACTIONS  # TODO 测试用
        self.state = WSState.Closed

        self._session_id = ""

        self._heartbeat_interval = 0
        self._heartbeat_task: asyncio.Task = None

        self._user: User = None

    @cached_property
    def ReceivePayloadsType(self):
        return receive_payloads_type()

    async def handle(self, data: websockets.Data):
        try:
            payload = self.ReceivePayloadsType.validate_json(data)
            log.debug(f"{type(payload)!r} {payload.model_dump()}")
        except ValidationError as e:
            payload = None
            log.exception(f"raw: {data!r}, error:{e.json(include_url=False)!r}", exc_info=e)
        match payload:
            case HelloPayload():
                self._heartbeat_interval = payload.data.heartbeat_interval / 1000
                token = self.ws.bot._api._authorization
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
                        self._user = payload.data.user
                        self._start_heartbeat()
                        self.to_connected_session()
                    case ResumedEventPayload():
                        self._start_heartbeat()
                        self.to_connected_session()
                    case ChannelAtMessageEventPayload():
                        log.debug(f"收到消息：{payload.data!r}")
                        if payload.data.content.lower().endswith("hello"):
                            await self.ws.bot._api.channel_reply("全体目光向我看齐，我宣布个事儿！\nMQGA！", payload)
                    case ChannelMessageReactionAddEventPayload():
                        if self._user.id != payload.data.user_id:
                            log.debug(f"收到表情表态：{payload.data!r}")
                            if all(self._user.id != user.id for user in 
                                   await self.ws.bot._api.channel_reaction_get_head_users(payload.data, payload.data.emoji)):
                                log.debug("自己也贴个表情…")
                                await self.ws.bot._api.channel_reaction(payload.data, payload.data.emoji)
                        else:
                            log.debug(f"收到自己的表情表态：{payload.data!r}")
                    case ChannelMessageReactionRemoveEventPayload():
                        if self._user.id != payload.data.user_id:
                            log.debug(f"表情表态被取消：{payload.data!r}")
                            if any(self._user.id == user.id for user in 
                                   await self.ws.bot._api.channel_reaction_get_head_users(payload.data, payload.data.emoji)):
                                log.debug("也取消自己贴的表情…")
                                await self.ws.bot._api.channel_reaction_delete(payload.data, payload.data.emoji)
                        else:
                            log.debug(f"自己的表情表态被取消：{payload.data!r}")
                        
            case InvalidSessionPayload():
                self._session_id = ""
            case HeartbeatAckPayload() | ReconnectPayload():
                pass

    __call__ = handle

    def to_connecting(self):
        self.state = WSState.Connecting
    
    def to_connected_raw(self):
        self.state = WSState.ConnectedRaw

    def to_connected_session(self):
        self.state = WSState.ConnectedSession
    
    def to_closed(self):
        self.state = WSState.Closed

    async def _send_payload(self, payload: Payload):
        log.debug(payload.model_dump(by_alias=True))
        await self.ws.client.send(payload.model_dump_json(by_alias=True))

    def _start_heartbeat(self):
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._heartbeat_task.add_done_callback(self.ws._task_done)

    async def _heartbeat_loop(self):
        log.info("心砰砰地跳")
        while self.ws.client.open:
            await self.heartbeat()
            await asyncio.sleep(self._heartbeat_interval)

    async def heartbeat(self):
        await self._send_payload(HeartbeatPayload(data=self._last_seq_no or None))
