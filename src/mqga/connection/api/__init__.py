from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot
    from mqga.q.payload import EventPayload
    from mqga.q.api import FileInfo
    from mqga.q.api import MarkdownTemplate, MarkdownCustom, KeyboardTemplate, KeyboardCustom

from mqga.q.constant import FileType

from mqga.connection.api.client import APIClient
from mqga.connection.api.source import ChannelAPI, GroupAPI, PrivateAPI

class API:

    def __init__(self, bot: Bot):
        self.bot = bot
        self.client = APIClient(bot)
        self._channel_api = ChannelAPI(self.client)
        self._group_api = GroupAPI(self.client)
        self._private_api = PrivateAPI(self.client)
        self._unified_api = super(GroupAPI, self._group_api)

    async def __aenter__(self):
        # 并不在这里初始化，而是在 bot 初始化时初始化
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.stop()

    async def init(self):
        await self.client.init()

    @property
    def channel(self):
        """ 频道 api """
        return self._channel_api

    @property
    def group(self):
        """ 群聊 api """
        return self._group_api
    
    @property
    def private(self):
        """ 私聊 api """
        return self._private_api

    def of(self, payload: EventPayload):
        """ 获取 payload 对应渠道的 api """
        for source in (self._channel_api, self._group_api, self._private_api):
            if source._payload_to_id(payload):
                return source
        raise ValueError(f"尚不支持把 {payload!r} 用于任何渠道的 api")

    async def reply_text(self, content: str, payload: EventPayload):
        """ 以文本回复消息、事件 """
        return await self.of(payload).reply_text(content, payload)

    async def reply_media(self, file_or_url: str | FileInfo, payload: EventPayload, content: str = "", file_type: FileType = FileType.图片):
        """ 以富媒体（图文等）回复消息、事件 """
        return await self.of(payload).reply_media(file_or_url, payload, content, file_type)

    async def reply_md(self, payload: EventPayload, markdown: MarkdownTemplate | MarkdownCustom | None = None, keyboard: KeyboardTemplate | KeyboardCustom | None = None):
        """ 
            以 markdown 回复消息、事件\n
            keyboard 为消息底部挂载的按钮
        """
        return await self.of(payload).reply_md(payload, markdown, keyboard)
        