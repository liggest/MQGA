from __future__ import annotations

from typing import Callable, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from mqga.event.manager import EventDispatcherType

T = TypeVar("T", bound=Callable)

from mqga.event.box import Box
from mqga.event.event import MultiEvent, PlainReturns
from mqga.event.dispatcher import EventPayloadDispatcher, MessageDispatcher
from mqga.event.dispatcher import ChannelAtMessageDispatcher, GroupAtMessageDispatcher, PrivateMessageDispatcher
from mqga.q.constant import EventType
from mqga.q.message import Emoji
from mqga.q.payload import EventPayload

EmojiEvent = MultiEvent[[], Emoji | PlainReturns]

def _deco_init(func: T):
    """ 装饰器首先执行的逻辑 """
    from mqga.lookup.context import context
    box = Box(func)
    return context, box

def _deco_init_dispatcher(func: T, cls: type[EventDispatcherType]):
    """ 装饰器首先执行的逻辑，带 Dispatcher """
    context, box = _deco_init(func)
    return context, box, context.bot._em.ensure(cls)
# class On:

#     def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
#         return func

class OnMessage:

    def __init__(self, dispatcher_type: type[MessageDispatcher]) -> None:
        """ dispatcher_type 用于接收消息的 Dispatcher 类，None 代表接收全体消息 """
        self.dispatcher_type = dispatcher_type

    def _deco_init_dispatcher(self, func: T):
        """ 装饰器首先执行的逻辑 """
        context, box = _deco_init(func)
        if self.dispatcher_type is MessageDispatcher:
            return context, box, context.bot._em._all_message_dispatcher
        return context, box, context.bot._em.ensure(self.dispatcher_type)
        
    def __call__(self, func: Callable[[], str]):
        context, box, dispatcher = self._deco_init_dispatcher(func)
        # context.bot._em.events.message.register(box)
        dispatcher.register_message(box, context.bot)
        return func

    def full_match(self, content: str):
        """ 完全匹配 content """
        def inner(func: Callable[[], str]):
            context, box, dispatcher = self._deco_init_dispatcher(func)
            dispatcher.register_full_match(box, context.bot, content)
            # context.bot._em.events.message_full_match(content).register(box)
            # parent = dispatcher._message_event
            # event = parent.full_match_events.get(content) or StrEvent(f"qq_message_full_match_{content!r}", parent)
            # event.register(box)
            # parent.full_match_events.__setitem__(content, event)
            return func
        return inner
    
    def regex(self, content: str):
        def inner(func: Callable[[], str]):
            context, box, dispatcher = self._deco_init_dispatcher(func)
            dispatcher.register_regex(box, context.bot, content)
            # event = StrEvent(f"message_regex_{content!r}")
            # event.register(box)
            # context.bot._em.events.message_regex.append((re.compile(content), event))
            return func
        return inner

    def filter_by(self, filter: Callable[[], bool]):
        def inner(func: Callable[[], str]):
            context, box, dispatcher = self._deco_init_dispatcher(func)
            dispatcher.register_filter_by(box, context.bot, filter)
            # event = StrEvent(f"message_filter_by_{filter!r}")
            # event.register(box)
            # context.bot._em.events.message_filter_by.append((filter, event))
            return func
        return inner

# TODO: 暂时先这样，之后往 with 的方向改

on_message = OnMessage(MessageDispatcher)

on_channel_message = OnMessage(ChannelAtMessageDispatcher)
    
on_group_message = OnMessage(GroupAtMessageDispatcher)

on_private_message = OnMessage(PrivateMessageDispatcher)

class OnEventPayload:

    def __call__(self, func: Callable[[], str]):
        context, box = _deco_init(func)
        # context.bot._em._root_event.payload_event.event_payload_event.register(box)
        context.bot._em.events.payload_of(EventPayload).register(box)
        return func

    def of(self, type: EventType):
        if not (dispatcher_type := EventPayloadDispatcher._subs.get(type)):
            raise ValueError(f"尚不支持处理 {type!r} 的事件")
        
        def inner(func: Callable[[], Emoji]):
            context, box, dispatcher = _deco_init_dispatcher(func, dispatcher_type)
            dispatcher: EventPayloadDispatcher
            dispatcher.register(box, context.bot, None)  # 注册到特定的 EventPayloadDispatcher 子类
            # parent = context.bot._em._root_event.payload_event.event_payload_event
            # payload_type = dispatcher._payload_type
            # context.bot._em.events.payload_of(payload_type).register(box)
            # event = parent.of(payload_type) or EmojiEvent(f"event_payload_{payload_type!r}", parent)
            # event.register(box)
            # parent.event_events.__setitem__(payload_type, event)
            return func
        
        return inner

on_event = OnEventPayload()

# @on_channel_message.full_match("hello")
# def on_message_default():
#     return "Hello World!"

