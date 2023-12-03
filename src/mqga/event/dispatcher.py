from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, TypeVar, Generic, get_origin, get_args, Iterable, Generator, Callable
import inspect
import re

if TYPE_CHECKING:
    from mqga.bot import Bot
    from mqga.event.manager import Manager
    from mqga.event.space import MessageSpace
    from mqga.q.message import Message

from mqga.log import log
from mqga.event.event import Box, Params, ReturnT, Event, StrEvent
# from mqga.event.event import PlainReturns
from mqga.q.constant import EventType, OpCode
from mqga.q.constant import Intents, EventType2Intent
from mqga.q.message import Emoji
from mqga.q.payload import Payload, EventPayload, ChannelAtMessageEventPayload
from mqga.q.payload import ChannelMessageReactionAddEventPayload, ChannelMessageReactionRemoveEventPayload
from mqga.q.payload import GroupAtMessageEventPayload, PrivateMessageEventPayload

MessageEventPayload = ChannelAtMessageEventPayload | GroupAtMessageEventPayload | PrivateMessageEventPayload

T = TypeVar("T")
PayloadT = TypeVar("PayloadT", bound=Payload)
EventPayloadT = TypeVar("EventPayloadT", bound=EventPayload)
MessageEventPayloadT = TypeVar("MessageEventPayloadT", bound=MessageEventPayload)

class Dispatcher(Generic[T, Params, ReturnT]):

    def __init__(self, manager: Manager):
        pass

    async def is_accept(self, bot: Bot, target: T) -> bool:
        # TODO
        raise NotImplementedError

    async def _pre_dispatch(self, bot: Bot, target: T):
        pass

    async def emit(self, bot: Bot, target: T, *args: Params.args, **kw: Params.kwargs) -> Iterable[ReturnT]:
        return []

    async def _handle_emit(self, result: ReturnT, bot: Bot, target: T):
        if inspect.isawaitable(result):
            bot._em.background_task(result)  # 回调返回的可等待对象，送去后台执行

    async def _post_dispatch(self, bot: Bot, target: T):
        pass

    async def dispatch(self, bot: Bot, target: T, *args: Params.args, **kw: Params.kwargs):
        await self._pre_dispatch(bot, target)

        for result in await self.emit(bot, target, *args, **kw):
            await self._handle_emit(result, bot, target)
        
        await self._post_dispatch(bot, target)
        
    def register(self, box: Box[Params, ReturnT], bot: Bot, target: T):
        pass

class EventDispatcher(Dispatcher[Event[Params, ReturnT], Params, ReturnT]):

    # async def is_accept(self, bot, target) -> bool:
    #     # TODO
    #     raise NotImplementedError

    # async def _pre_dispatch(self, bot, target):
    #     pass

    # async def _handle_emit(self, result, bot, target):
    #     pass

    # async def _post_dispatch(self, bot, target):
    #     pass

    async def emit(self, bot, target, *args, **kw):
        return await target.emit(*args, **kw)
    
    # async def dispatch(self, bot, target, *args, **kw):
    #     await self._pre_dispatch(bot, target)

    #     for result in await self.emit(bot, target, *args, **kw):
    #         await self._handle_emit(result, bot, target)
        
    #     await self._post_dispatch(bot, target)
        
    def register(self, box, bot, target):
        return target.register(box)

class PayloadDispatcherMeta(type):

    def __new__(meta, name: str, bases: tuple[type, ...], attrs: dict):
        if original_bases := attrs.get("__orig_bases__"):
            # original_bases: tuple[type, ...]
            _payload_type = meta._payload_type_in_bases(original_bases)
            if _payload_type:
                # 自动填充 PayloadDispatcher 子类的 _payload_type、_event_type
                # 以及 EventPayloadDispatcher 子类的 _intent
                attrs["_payload_type"] = _payload_type
                fields = _payload_type.model_fields
                if _payload_type is Payload or _payload_type is EventPayload:
                    _type = None
                elif issubclass(_payload_type, EventPayload):
                    _type = fields["type"].default  # EventType
                    attrs["_intent"] = EventType2Intent[_type].intent
                else:
                    _type = fields["op_code"].default
                attrs["_type"] = _type  # OpCode
        return super().__new__(meta, name, bases, attrs)
    
    @classmethod
    def _payload_type_in_bases(meta, bases: tuple[type, ...]):
        """ 在 bases 中寻找 PayloadDispatcher[XXXPayload] 中的 XXXPayload """
        for base in bases:
            origin = get_origin(base)
            if not (isinstance(origin, type) and origin is not Generic and issubclass(origin, Generic)):
                continue
            args = get_args(base)
            if args and isinstance(arg := args[0], type) and issubclass(arg, Payload):
                return arg

# 所有 Payload 事件暂时都不接收参数
class PayloadDispatcher(Dispatcher[PayloadT, [], ReturnT], metaclass=PayloadDispatcherMeta):
    _payload_type = Payload
    _type: OpCode | None = None

    @staticmethod
    def flatten(iter_iters: Iterable[Iterable[ReturnT]]) -> Generator[ReturnT, None, None]:
        return (item for it in iter_iters if it for item in it if item is not None)

    @classmethod
    def _payload_event(cls, bot: Bot):
        return bot._em.events._payload_dict.get(cls._payload_type)
        # return bot._em._root_event.payload_event.event_payload_event.of(cls._payload_type)

    # async def is_accept(self, bot: Bot, target: PayloadT) -> bool:
    #     return await super().is_accept(bot, target)
    
    async def _pre_dispatch(self, bot: Bot, target: PayloadT):
        bot._context.payload = target

    async def emit(self, bot: Bot, target: PayloadT) -> Iterable[ReturnT]:
        """ 如果有注册对应的 PayloadEvent，触发之 """
        if event := self._payload_event(bot):
            return await event.emit()
        return []

    # async def _handle_emit(self, result, bot, target):
    #     pass

    # async def _post_dispatch(self, bot, target):
    #     pass

    # async def dispatch(self, bot, target):
    #     await self._pre_dispatch(bot, target)

    #     for result in await self.emit(bot, target):
    #         await self._handle_emit(result, bot, target)
        
    #     await self._post_dispatch(bot, target)

    def register(self, box: Box[[], ReturnT], bot: Bot, target: PayloadT):
        # if event := self._payload_event(bot):
            # event.register(box)
        bot._em.events.payload_of(self._payload_type).register(box)

    
class EventPayloadDispatcher(PayloadDispatcher[EventPayloadT, ReturnT]):
    
    _payload_type = EventPayload
    _type: EventType | None = None
    _intent: Intents = Intents.NONE

    _subs: dict[EventType, type[EventPayloadDispatcher]] = {}

    def __init_subclass__(subcls, **kw):
        super().__init_subclass__(**kw)  # 执行 Generic 的 __init_subclass__
        if not subcls._type:
            return
        if old_sub := subcls._subs.get(subcls._type):
            log.warning(f"{subcls!r} 覆盖了 {old_sub!r}")
        subcls._subs[subcls._type] = subcls

# TODO 改进写法
class MessageDispatcher(EventPayloadDispatcher[MessageEventPayloadT, str]):
    
    # def __init__(self, manager: Manager):
    #     self._message_event = manager._root_event.qq_event.message_event

    @classmethod
    def _message_space(cls, bot: Bot):
        return bot._em.events.all_message

    async def _pre_dispatch(self, bot: Bot, target: MessageEventPayloadT):
        await super()._pre_dispatch(bot, target)
        bot._context.message = target.data
    
    def _message_emit_coros(self, bot: Bot, message: Message):
        """ 触发各种消息事件 """
        self_space = self._message_space(bot)
        yield self.full_match_emit(self_space, message)
        yield self.regex_emit(self_space, message)
        yield self.filter_emit(self_space, message)
        yield self.message_emit(self_space, message)

    def _emit_coros(self, bot: Bot, target: MessageEventPayloadT):
        message = target.data
        yield from self._message_emit_coros(bot, message)  # 触发当前 dispatcher 的各种消息事件
        if self is not (all_dispatcher := bot._em._all_message_dispatcher):  # 当前 dispatcher 不是 all_message
            yield from all_dispatcher._message_emit_coros(bot, message)  # 触发当前 all_message 的各种消息事件
        yield super().emit(bot, target)

    async def emit(self, bot, target) -> Iterable[str]:
        return self.flatten(await asyncio.gather(*self._emit_coros(bot, target)))
    
    async def full_match_emit(self, space: MessageSpace, message: Message):
        # events = self._message_event._full_match_events
        # events = bot._em.events._message_full_match_dict
        events = space._full_match_dict
        if events and (event := events.get(message.content)):
            return await event.emit()

    async def regex_emit(self, space: MessageSpace, message: Message):
        # events = self._message_event._regex_events
        # events = bot._em.events.message_regex
        events = space.regex
        if events:
            coros = (event.emit() for pattern, event in events if pattern.search(message.content))
            return self.flatten(await asyncio.gather(*coros))

    async def filter_emit(self, space: MessageSpace, message: Message):
        # events = self._message_event._filter_events
        # events = bot._em.events.message_filter_by
        events = space.filter_by
        if events:
            coros = (event.emit() for is_accept, event in events if is_accept())
            return self.flatten(await asyncio.gather(*coros))

    async def message_emit(self, space: MessageSpace, message: Message):
        # event = self._message_event
        # event = bot._em.events.message
        event = space.any
        # if not (event._full_match_events and event._regex_events and event._filter_events):
        return await event.emit()

    async def _handle_emit(self, result, bot: Bot, target: MessageEventPayloadT):
        if isinstance(result, str):
            return await self._reply_str(result, bot, target)
        return await super()._handle_emit(result, bot, target)

    async def _reply_str(self, content: str, bot: Bot, payload: MessageEventPayloadT):
        dispatcher: MessageDispatcher = bot._em._dispatchers[payload.type]  # 回复来自各个渠道的消息
        if self is dispatcher:
            return {}
        return await dispatcher._reply_str(content, bot, payload)

    # def register(self, box, bot: Bot, target: MessageEventPayloadT):
    #     super().register(box, bot, target)

    # def register(self, box, bot, target):
    #     super().register(box, bot, target)
    #     # self._message_event.register(box)
    #     bot._em.events.message.register(box)
    def register_message(self, box: Box, bot: Bot):
        self._message_space(bot).any.register(box)

    def register_full_match(self, box: Box, bot: Bot, content: str):
        self._message_space(bot).full_match(content).register(box)

    def register_regex(self, box: Box, bot: Bot, content: str):
        space = self._message_space(bot)
        event = StrEvent(f"{space.source}_message_regex_{content!r}")
        event.register(box)
        space.regex.append((re.compile(content), event))

    def register_filter_by(self, box: Box, bot: Bot, filter: Callable[[], bool]):
        space = self._message_space(bot)
        event = StrEvent(f"{space.source}_message_filter_by_{filter!r}")
        event.register(box)
        space.filter_by.append((filter, event))

class ChannelAtMessageDispatcher(
    MessageDispatcher[ChannelAtMessageEventPayload]
):

    @classmethod
    def _message_space(cls, bot):
        return bot._em.events.channel_message

    # @staticmethod
    # def flatten(iter_iters: Iterable[Iterable[T]]) -> Generator[T, None, None]:
    #     return (item for it in iter_iters if it for item in it if item is not None)

    # def __init__(self, manager: Manager):
    #     self._message_event = manager._root_event.qq_event.message_event

    # async def _handle_emit(self, result, bot, target):
    #     return await bot._api.channel_reply(result, target)

    async def _reply_str(self, content, bot, payload):
        return await bot._api.channel.reply_text(content, payload)

    # async def dispatch(self, bot, payload):
    #     await super().dispatch(bot, payload)
    #     context = bot._context
    #     context.message = payload.data

    #     for result in await self.emit(bot, payload):
    #         await bot._api.channel_reply(result, payload)
        
    #     return True

# TODO 改进写法
class GroupAtMessageDispatcher(
    MessageDispatcher[GroupAtMessageEventPayload]
):
    @classmethod
    def _message_space(cls, bot):
        return bot._em.events.group_message

    async def _reply_str(self, content, bot, payload):
        return await bot._api.group.reply_text(content, payload)

# TODO 改进写法
class PrivateMessageDispatcher(
    MessageDispatcher[PrivateMessageEventPayload]
):
    @classmethod
    def _message_space(cls, bot):
        return bot._em.events.private_message

    async def _reply_str(self, content, bot, payload):
        return await bot._api.private.reply_text(content, payload)

# TODO 改进写法
class ChannelMessageReactionAddDispatcher(
    EventPayloadDispatcher[ChannelMessageReactionAddEventPayload, Emoji]
):

    async def _handle_emit(self, result, bot, target):
        if isinstance(result, Emoji):
            return await bot._api.channel.reaction(target.data, result)
        return await super()._handle_emit(result, bot, target)

# TODO 改进写法
class ChannelMessageReactionRemoveDispatcher(
    EventPayloadDispatcher[ChannelMessageReactionRemoveEventPayload, Emoji]
):
    
    async def _handle_emit(self, result, bot, target):
        if isinstance(result, Emoji):
            return await bot._api.channel.reaction_delete(target.data, result)
        return await super()._handle_emit(result, bot, target)
