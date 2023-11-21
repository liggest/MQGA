from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING, TypeVar, Generic, get_origin, get_args, Iterable, Generator

if TYPE_CHECKING:
    from mqga.bot import Bot
    from mqga.event.manager import Manager
    from mqga.event.box import Box
    from mqga.event.event import Event
    from mqga.q.constant import EventType
    from mqga.q.message import Message

from mqga.log import log
from mqga.q.constant import Intents, EventType2Intent
from mqga.q.message import Emoji
from mqga.q.payload import EventPayload, ChannelAtMessageEventPayload
from mqga.q.payload import ChannelMessageReactionAddEventPayload, ChannelMessageReactionRemoveEventPayload
from mqga.q.payload import GroupAtMessageEventPayload, PrivateMessageEventPayload

MessageEventPayload = ChannelAtMessageEventPayload | GroupAtMessageEventPayload | PrivateMessageEventPayload

T = TypeVar("T")
EventPayloadT = TypeVar("EventPayloadT", bound=EventPayload)

class DispatcherMeta(type):

    def __new__(meta, name: str, bases: tuple[type, ...], attrs: dict):
        if original_bases := attrs.get("__orig_bases__"):
            original_bases: tuple[type, ...]
            _payload_type = meta._payload_type_in_bases(original_bases)
            if _payload_type:
                # 自动填充 Dispatcher 子类的 _payload_type、_event_type、_intent
                attrs["_payload_type"] = _payload_type
                event_type: EventType = _payload_type.model_fields["type"].default
                attrs["_event_type"] = event_type
                attrs["_intent"] = EventType2Intent[event_type].intent
        return super().__new__(meta, name, bases, attrs)
    
    @classmethod
    def _payload_type_in_bases(meta, bases: tuple[type, ...]):
        """ 在 bases 中寻找 Dispatcher[XXXEventPayload] 中的 XXXEventPayload """
        for base in bases:
            origin = get_origin(base)
            if not (isinstance(origin, type) and origin is not Generic and issubclass(origin, Generic)):
                continue
            args = get_args(base)
            if args and isinstance(arg := args[0], type) and issubclass(arg, EventPayload):
                return arg

class Dispatcher(Generic[EventPayloadT], metaclass=DispatcherMeta):
    
    _payload_type = EventPayload
    _event_type: EventType = None
    _intent: Intents = Intents.NONE

    _subs: dict[type[EventType], Dispatcher] = {}

    @classmethod
    def _event_payload_event(cls, bot: Bot):
        return bot._em._root_event.payload_event.event_payload_event.of(cls._payload_type)

    def __init__(self, manager: Manager):
        pass

    def __init_subclass__(subcls):
        if subcls._event_type is Dispatcher._event_type:
            return
        if old_sub := subcls._subs.get(subcls._event_type):
            log.warning(f"{subcls!r} 覆盖了 {old_sub!r}")
        subcls._subs[subcls._event_type] = subcls

    async def is_accept(self, bot: Bot, payload: EventPayloadT, event: Event) -> bool:
        # TODO
        raise NotImplementedError

    async def _pre_dispatch(self, bot: Bot, payload: EventPayloadT):
        bot._context.payload = payload

    async def _handle_emit(self, result: T, bot: Bot, payload: EventPayloadT):
        pass

    async def _post_dispatch(self, bot: Bot, payload: EventPayloadT):
        pass

    async def dispatch(self, bot: Bot, payload: EventPayloadT):
        await self._pre_dispatch(bot, payload)

        for result in await self.emit(bot, payload):
            await self._handle_emit(result, bot, payload)
        
        await self._post_dispatch(bot, payload)
        
    async def emit(self, bot: Bot, payload: EventPayloadT) -> Iterable[T]:
        if event := self._event_payload_event(bot):
            return await event.emit()
        
    def register(self, bot: Bot, box: Box):
        if event := self._event_payload_event(bot):
            event.register(box)

# TODO 改进写法
class MessageDispatcher(Dispatcher):

    @staticmethod
    def flatten(iter_iters: Iterable[Iterable[T]]) -> Generator[T, None, None]:
        return (item for it in iter_iters if it for item in it if item is not None)
    
    def __init__(self, manager: Manager):
        self._message_event = manager._root_event.qq_event.message_event

    async def _pre_dispatch(self, bot, payload: MessageEventPayload):
        await super()._pre_dispatch(bot, payload)
        context = bot._context
        context.message = payload.data

    async def emit(self, bot, payload: MessageEventPayload) -> Iterable[str]:
        message = payload.data
        return self.flatten(await asyncio.gather(
            self.full_match_emit(bot, message),
            self.regex_emit(bot, message),
            self.filter_emit(bot, message),
            self.fallback_emit(bot, message),
            super().emit(bot, payload)
        ))
        
    async def full_match_emit(self, bot: Bot, message: Message):
        events = self._message_event._full_match_events
        if events and (event := events.get(message.content)):
            return await event.emit()

    async def regex_emit(self, bot: Bot, message: Message):
        events = self._message_event._regex_events
        if events:
            return self.flatten(await asyncio.gather(
                *(event.emit() for pattern, event in events if pattern.search(message.content))
            ))

    async def filter_emit(self, bot: Bot, message: Message):
        events = self._message_event._filter_events
        if events:
            return self.flatten(await asyncio.gather(
                *(event.emit() for is_accept, event in events if is_accept(message))
            ))

    async def fallback_emit(self, bot: Bot, message: Message):
        event = self._message_event
        if not (event._full_match_events and event._regex_events and event._filter_events):
            return await event.emit()

    def register(self, bot, box):
        super().register(bot, box)
        self._message_event.register(box)

class ChannelAtMessageDispatcher(MessageDispatcher[ChannelAtMessageEventPayload]):

    # @staticmethod
    # def flatten(iter_iters: Iterable[Iterable[T]]) -> Generator[T, None, None]:
    #     return (item for it in iter_iters if it for item in it if item is not None)

    # def __init__(self, manager: Manager):
    #     self._message_event = manager._root_event.qq_event.message_event

    async def _handle_emit(self, result: str, bot, payload):
        return await bot._api.channel_reply(result, payload)

    # async def dispatch(self, bot, payload):
    #     await super().dispatch(bot, payload)
    #     context = bot._context
    #     context.message = payload.data

    #     for result in await self.emit(bot, payload):
    #         await bot._api.channel_reply(result, payload)
        
    #     return True

# TODO 改进写法
class ChannelMessageReactionAddDispatcher(Dispatcher[ChannelMessageReactionAddEventPayload]):

    async def _handle_emit(self, result, bot, payload):
        if isinstance(result, Emoji):
            return await bot._api.channel_reaction(payload.data, result)

# TODO 改进写法
class ChannelMessageReactionRemoveDispatcher(Dispatcher[ChannelMessageReactionRemoveEventPayload]):
    
    async def _handle_emit(self, result, bot, payload):
        if isinstance(result, Emoji):
            return await bot._api.channel_reaction_delete(payload.data, result)

# TODO 改进写法
class GroupAtMessageDispatcher(MessageDispatcher[GroupAtMessageEventPayload]):

    async def _handle_emit(self, result: str, bot, payload):
        return await bot._api.group_reply(result, payload)

# TODO 改进写法
class PrivateMessageDispatcher(MessageDispatcher[PrivateMessageEventPayload]):

    async def _handle_emit(self, result: str, bot, payload):
        return await bot._api.private_reply(result, payload)
