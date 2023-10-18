from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqga.bot import Bot

from mqga.log import log

class Payload:  # TODO 重要：决定这是一个什么东西（纯 dict？ dict 子类？ MutableMapping 子类？ dataclass？ BaseModel？ TypedDict?）
    pass

class WS:

    def __init__(self, bot:Bot):
        self.bot = bot
        raise NotImplementedError   # TODO

    async def init(self):
        log.info(f"WS 初始化")
        # TODO GET /gateway
        raise NotImplementedError
