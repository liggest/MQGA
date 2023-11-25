from __future__ import annotations

from functools import reduce
import operator
import asyncio

from typing import TYPE_CHECKING, TypeVar, Coroutine

if TYPE_CHECKING:
    from mqga.bot import Bot
    from mqga.q.constant import EventType

from mqga.log import log
from mqga.event.dispatcher import EventPayloadDispatcher
# from mqga.event.tree import RootEvent
from mqga.event.space import Space
from mqga.q.payload import EventPayload
from mqga.q.constant import Intents

DispatcherType = TypeVar("DispatcherType", bound=EventPayloadDispatcher)

class Manager:

    def __init__(self, bot: Bot):
        self.bot = bot
        self._dispatchers: dict[EventType, EventPayloadDispatcher] = {}
        # self._root_event = RootEvent()
        self.events: Space = Space()
        self._default_dispatcher = EventPayloadDispatcher(self)
        self._tasks = set()

    async def dispatch(self, payload: EventPayload):
        if dispatcher := self._dispatchers.get(payload.type):
            await dispatcher.dispatch(self.bot, payload)
            log.debug(f"{payload.type} 事件分发成功")
            return
        # self.bot._context.payload = payload
        # await self._root_event.payload_event.event_payload_event.emit()  # 没找到 dispatcher 也向上传播
        await self._default_dispatcher.dispatch(self.bot, payload)  # 任意 EventPayload
        log.warning(f"未能分发 {payload.type} 事件！")

    def ensure(self, cls: type[DispatcherType]) -> DispatcherType:
        if dispatcher := self._dispatchers.get(cls._type):
            return dispatcher
        self._dispatchers[cls._type] = dispatcher = cls(self)
        return dispatcher

    @property
    def intents(self) -> Intents:
        """ 当前创建的所有 dispatcher 对应事件的意向之和 """
        return reduce(operator.or_, (dispatcher._intent for dispatcher in self._dispatchers.values()), Intents.DEFAULT) 

    def _task_done(self, task: asyncio.Task):
        self._tasks.remove(task)
        if task.cancelled():
            log.warning(f"后台任务 {task!r} 被取消")
        elif e := task.exception():
            log.exception(f"后台任务 {task!r} 失败", exc_info=e)

    def background_task(self, coro: Coroutine):
        """ 让 coro 作为任务在后台执行 """
        if not isinstance(coro, asyncio.Task):
            coro = asyncio.create_task(coro)
        self._tasks.add(coro)
        coro.add_done_callback(self._task_done)
