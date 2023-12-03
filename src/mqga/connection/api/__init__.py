from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot

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
