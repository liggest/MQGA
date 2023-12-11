from __future__ import annotations

from typing import TypeVar, Generic, Iterable, AsyncGenerator, Callable

from abc import ABCMeta, abstractmethod

from collections import deque, defaultdict
import asyncio

from mqga.event.box import Box, ReturnT, Params
from mqga.log import log

# Params = ParamSpec("P")
# ReturnT = TypeVar("T")
# EventT = TypeVar("EventT", bound="Event")

class Event(Generic[Params, ReturnT], metaclass=ABCMeta):
    """ 事件基类 """

    name = ""

    def __init__(self, name=""):
        if name:
            self.name = name
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"
    
    @property
    @abstractmethod
    def callbacks(self) -> Iterable[Box[Params, ReturnT]]:
        raise NotImplementedError
    
    @abstractmethod
    def register(self, callback: Box[Params, ReturnT]) -> None:
        raise NotImplementedError

    @abstractmethod
    def unregister(self, callback: Box[Params, ReturnT]) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def _emit_gen(self, *args: Params.args, **kw: Params.kwargs) -> AsyncGenerator[ReturnT, None]:
        raise NotImplementedError
        yield

    async def emit(self, *args: Params.args, **kw: Params.kwargs) -> list[ReturnT]:
        return [r async for r in self._emit_gen(*args, **kw)]
    
    def _error(self, e: Exception):
        log.exception(f"Emit error in {self!r}", exc_info=e)

class MultiEvent(Event[Params, ReturnT]):
    """ 触发一组回调的事件 """

    def __init__(self, name=""):
        super().__init__(name)
        self._callbacks: deque[Box[Params, ReturnT]] | None = None
    
    @property
    def callbacks(self):
        if self._callbacks is None:
            self._callbacks = deque()
        return self._callbacks

    def register(self, callback):
        self.callbacks.append(callback)
    
    def unregister(self, callback):
        if not self._callbacks:
           return False
        try:
            self.callbacks.remove(callback)
            return True
        except ValueError:
            return False

    async def _emit_gen(self, *args, **kw) -> AsyncGenerator[ReturnT, None]:
        if not self._callbacks:
           return
        
        coros = (call(*args, **kw) for call in self.callbacks)
        results: list[ReturnT | Exception] = await asyncio.gather(*coros, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                self._error(r)
            else:
                yield r

class SingleEvent(Event[Params, ReturnT]):
    """ 触发唯一回调的事件 """

    def __init__(self, name=""):
        super().__init__(name)
        self._callback: Box[Params, ReturnT] | None = None
    
    @property
    def callbacks(self) -> list[Box[Params, ReturnT]]:
        if self._callback:
            return [self._callback]
        return []

    def register(self, callback):
        self._callback = callback

    def unregister(self, callback):
        if not self._callback:
            return False
        if success := (self._callback == callback):
            self._callback = None
        return success

    async def _emit_gen(self, *args, **kw) -> AsyncGenerator[ReturnT, None]:
        if not self._callback:
            return
        
        try:
            r = await self._callback(*args, **kw)
        except Exception as e:
            self._error(e)
            return
        
        yield r

PairLeft = TypeVar("PairLeft")
PairRight = TypeVar("PairRight")
Pair = tuple[PairLeft, PairRight]
# class Pair(tuple[PairLeft, PairRight]):

#     def __new__(cls, left: PairLeft, right: PairRight):
#         return super().__new__(cls, (left, right))

#     @property
#     def left(self) -> PairLeft:
#         return self[0]

#     @property
#     def right(self) -> PairRight:
#         return self[1]

#     def __repr__(self):
#         return f"{self.__class__.__name__}({self.left!r}, {self.right!r})"

RuleT = TypeVar("RuleT")

class RuleEvent(Generic[RuleT, Params, ReturnT], Event[Params, ReturnT]):
    """ 附带规则的事件 """

    @property
    @abstractmethod
    def callbacks(self) -> Iterable[Pair[RuleT | Callable[[RuleT], bool], Box[Params, ReturnT]]]:
        raise NotImplementedError

    @abstractmethod
    def register(self, rule: RuleT | Callable[[RuleT], bool], callback: Box[Params, ReturnT]) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def unregister(self, rule: RuleT | Callable[[RuleT], bool] | None, callback: Box[Params, ReturnT] | None) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    async def _emit_gen(self, rule_arg: RuleT, *args: Params.args, **kw: Params.kwargs) -> AsyncGenerator[ReturnT, None]:
        raise NotImplementedError
        yield
    
    async def emit(self, rule_arg: RuleT, *args: Params.args, **kw: Params.kwargs) -> list[ReturnT]:
        return [r async for r in self._emit_gen(rule_arg, *args, **kw)]

class RuleMultiEvent(RuleEvent[RuleT, Params, ReturnT]):
    """ 根据规则触发一组回调的事件 """

    def __init__(self, name=""):
        super().__init__(name)
        self._callbacks: deque[Pair[RuleT | Callable[[RuleT], bool], Box[Params, ReturnT]]] | None = None

    @property
    def callbacks(self):
        if self._callbacks is None:
            self._callbacks = deque()
        return self._callbacks

    def register(self, rule: RuleT | Callable[[RuleT], bool], callback: Box[Params, ReturnT]) -> None:
        self.callbacks.append((rule, callback))

    def unregister(self, rule: RuleT | Callable[[RuleT], bool] | None, callback: Box[Params, ReturnT] | None) -> bool:
        """ 查找并移除 (rule, callback)。rule 和 callback 的其一可以为 None，届时将先遍历查找对应的另一项，之后再移除 """
        if not self._callbacks:
           return False
        pair = None
        if rule is None:
            any(pair := p for p in self.callbacks if p[1] is callback)
        elif callback is None:
            any(pair := p for p in self.callbacks if p[0] == rule)
        else:
            pair = (rule, callback)
        try:
            self.callbacks.remove(pair)
            return True
        except ValueError:
            return False

    def _is_accept(self, rule: RuleT | Callable[[RuleT], bool], rule_arg: RuleT):
        return rule == rule_arg or rule(rule_arg) if callable(rule) else False

    def _emit_coros(self, rule_arg: RuleT, *args: Params.args, **kw: Params.kwargs):
        for rule, call in self.callbacks:
            if self._is_accept(rule, rule_arg):
                # yield call(*args, **kw)
                yield asyncio.create_task(call(*args, **kw))  # 这样在 _is_accept 里面可以设置一些 context 的值

    async def _emit_gen(self, rule_arg: RuleT, *args: Params.args, **kw: Params.kwargs) -> AsyncGenerator[ReturnT, None]:
        if not self._callbacks:
           return
        
        coros = self._emit_coros(rule_arg, *args, **kw)
        results: list[ReturnT | Exception] = await asyncio.gather(*coros, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                self._error(r)
            else:
                yield r

class EventGroup(Event[Params, ReturnT]):
    """ 事件组，触发多个事件 """

    def __init__(self, name="", events: Iterable[Event[Params, ReturnT]] | None = None):
        super().__init__(name)
        self._callbacks: deque[Event[Params, ReturnT]] | None = deque(events) if events is not None else None

    @property
    def callbacks(self):
        if self._callbacks is None:
            self._callbacks = deque()
        return self._callbacks

    def register(self, callback):
        self.callbacks[-1].register(callback)  # TODO 不知道这样好不好

    def unregister(self, callback):
        if not self._callbacks:
           return False
        success = False
        for event in self.callbacks:
            if event.unregister(callback):
                success = True
        return success

    async def _emit_gen(self, *args, **kw) -> AsyncGenerator[ReturnT, None]:
        if not self._callbacks:
           return
        
        coros = (event.emit(*args, **kw) for event in self.callbacks)
        result_lists: list[list[ReturnT] | Exception] = await asyncio.gather(*coros, return_exceptions=True)
        for rlist in result_lists:
            if isinstance(rlist, Exception):
                self._error(rlist)
            else:
                for result in rlist:
                    yield result

KeyT = TypeVar("KeyT")

# TODO 不知道这样好不好
class EventMap(Generic[KeyT, Params, ReturnT], Event[Params, ReturnT]):
    """ 事件组，触发键对应的事件 """

    _default_cls: type[Event[Params, ReturnT]] = MultiEvent[Params, ReturnT]
    """ 实际触发的事件的默认类型 """

    def __init__(self, name="", default_event_cls: type[Event[Params, ReturnT]] | None = None):
        super().__init__(name)
        self._callbacks: defaultdict[KeyT, Event[Params, ReturnT]] | None = None
        if default_event_cls:
            self._default_cls = default_event_cls

    @property
    def callbacks(self):
        if self._callbacks is None:
            self._callbacks = defaultdict(self._default_cls)
        return self._callbacks

    def register(self, key: KeyT, callback: Box[Params, ReturnT], in_event: Event[Params, ReturnT] | None = None):
        if in_event:
            if event := self.callbacks.get(key):
                raise ValueError(f"{self!r} 已经在 {key!r} 注册了 {event!r}，不能再注册 {in_event!r}")
            self.callbacks[key] = in_event
        self.callbacks[key].register(callback)

    def unregister(self, key: KeyT, callback: Box[Params, ReturnT]):
        if not self._callbacks:
            return False
        if not (event := self.callbacks.get(key)):
            return False
        return event.unregister(callback)

    async def _emit_gen(self, key: KeyT, *args: Params.args, **kw: Params.kwargs) -> AsyncGenerator[ReturnT, None]:
        if not self._callbacks:
            return
        if not (event := self.callbacks.get(key)):
            return

        async for r in event._emit_gen(*args, **kw):
            yield r
    
    async def emit(self, key: KeyT, *args: Params.args, **kw: Params.kwargs):
        return [r async for r in self._emit_gen(key, *args, **kw)]

from typing import Awaitable

PlainReturns = Awaitable[None] | None

PlainEvent = MultiEvent[[], PlainReturns]
StrEvent = MultiEvent[[], str | PlainReturns]
