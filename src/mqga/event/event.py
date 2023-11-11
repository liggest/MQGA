from __future__ import annotations

from typing import TypeVar, Generic

from collections import deque
import asyncio

from mqga.event.box import Box, ReturnT, Params

# Params = ParamSpec("P")
# ReturnT = TypeVar("T")
EventT = TypeVar("EventT", bound="Event")

class Event(Generic[Params, ReturnT]):

    name = "event"

    def __init__(self, name="", parent: EventT=None):
        if name:
            self.name = name
        self.parent = parent
        self._callbacks: deque[Box[Params, ReturnT]] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r}, {self.parent!r})"

    @property
    def callbacks(self):
        if self._callbacks is None:
            self._callbacks = deque()
        return self._callbacks

    def register(self, callback: Box[Params, ReturnT]):
        self.callbacks.append(callback)
    
    async def emit_gen(self, *args: Params.args, **kw: Params.kwargs):
        if self._callbacks:
           result: list[ReturnT] = await asyncio.gather(*(call(*args, **kw) for call in self.callbacks), return_exceptions=True)
           for r in result:
               yield r
        if self.parent:
            async for r in self.parent.emit_gen(*args, **kw):
                yield r

    async def emit(self, *args, **kw):
        return [r async for r in self.emit_gen(*args, **kw)]

PlainEvent = Event[[], None]
StrEvent = Event[[], str]
