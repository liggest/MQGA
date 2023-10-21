from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot

import websockets

from mqga.log import log

class WS:

    def __init__(self, bot:Bot):
        self.bot = bot
        # raise NotImplementedError   # TODO

    async def init(self):
        log.info(f"WS 初始化")
        # TODO GET /gateway
        # raise NotImplementedError
