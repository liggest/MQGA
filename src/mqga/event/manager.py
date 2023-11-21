from __future__ import annotations

from functools import reduce
import operator

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from mqga.bot import Bot
    from mqga.q.constant import EventType

from mqga.log import log
from mqga.event.dispatcher import Dispatcher
from mqga.event.tree import RootEvent
from mqga.q.payload import EventPayload
from mqga.q.constant import Intents

DispatcherType = TypeVar("DispatcherType", bound=Dispatcher)

class Manager:

    def __init__(self, bot: Bot):
        self.bot = bot
        self._dispatchers: dict[EventType, Dispatcher] = {}
        self._root_event = RootEvent()

    async def dispatch(self, payload: EventPayload):
        if dispatcher := self._dispatchers.get(payload.type):
            await dispatcher.dispatch(self.bot, payload)
            log.debug(f"{payload.type} 事件分发成功")
            return
        self.bot._context.payload = payload
        await self._root_event.payload_event.event_payload_event.emit()  # 没找到 dispatcher 也向上传播
        log.warning(f"未能分发 {payload.type} 事件！")

    def ensure(self, cls: type[DispatcherType]) -> DispatcherType:
        if dispatcher := self._dispatchers.get(cls._event_type):
            return dispatcher
        self._dispatchers[cls._event_type] = dispatcher = cls(self)
        return dispatcher

    @property
    def intents(self) -> Intents:
        return reduce(operator.or_, (dispatcher._intent for dispatcher in self._dispatchers.values()), Intents.DEFAULT) 
