from __future__ import annotations

from functools import cached_property
from types import ModuleType
# from collections import deque
# import re

from typing import Callable, get_args, overload, TYPE_CHECKING
from typing import TypeVar, Generic
if TYPE_CHECKING:
    from typing_extensions import Self

from mqga.event.event import Event, PlainEvent, StrEvent
from mqga.event.special import RegexEvent, FilterByEvent
from mqga.q.payload import Payload

EventT = TypeVar("EventT", bound=Event)

_Undefined = object()

class EventProperty(Generic[EventT]):

    def __init__(self, event_creator: type[EventT] | Callable[[object], EventT], name="") -> None:
        self._event_creator = event_creator
        self.name = name
        self._base_cls: type = None

    def __set_name__(self, cls, name: str):
        self.name = name
        self._base_cls = cls

    def __repr__(self):
        return f"{self.__class__.__name__}({self._event_creator!r}, name={self.name!r})"

    def _ensure_name(self):
        if not self.name:
            raise AttributeError(f"{self!r} 需要有个名字")

    @overload
    def __get__(self, obj: None, cls=None) -> Self:
        ...
    @overload
    def __get__(self, obj: object, cls=None) -> EventT:
        ...
    def __get__(self, obj, cls=None) -> EventT:
        if obj is None:  # 通过类访问属性
            return self
        self._ensure_name()
        val: EventT
        if (val := obj.__dict__.get(self.name, _Undefined)) is _Undefined:
            if isinstance(self._event_creator, type) or get_args(self._event_creator):  # 是 type 或 type[...]
                val = obj.__dict__[self.name] = self._event_creator(self.name)
            elif callable(self._event_creator):
                val = obj.__dict__[self.name] = self._event_creator(obj)
            else:
                raise AttributeError(f"无法通过 {self!r} 获得 {obj!r} 的 {self.name!r} 属性的值")
        return val

    def __set__(self, obj: object, value):
        self._ensure_name()
        obj.__dict__[self.name] = value

    def __delete__(self, obj: object):
        self._ensure_name()
        del obj.__dict__[self.name]

    def get_in(self, obj: object, default=None) -> EventT | None:
        """ 如果 obj 中还没有这个属性的值，返回 default """
        self._ensure_name()
        return obj.__dict__.get(self.name, default)
    
    def is_in(self, obj: object) -> bool:
        """ 判断 obj 中是否已经定义有了这个属性的值 """
        self._ensure_name()
        return self.name in obj.__dict__
    
    def ensure_in(self, obj: object) -> EventT:
        """ 如果 obj 中还没有这个属性的值，创建 """
        self._ensure_name()
        return self.__get__(obj, self._base_cls)

    # def __class_getitem__(cls, event_creator: type[EventT]) -> EventT:
    #     return super().__class_getitem__(event_creator)(event_creator)

class Space:

    payload = EventProperty(PlainEvent)
    """ 任意 Payload """

    @cached_property
    def _payload_dict(self) -> dict[type[Payload], PlainEvent]:
        return {}
    
    def payload_of(self, type: type[Payload]):
        """ 特定 Payload """
        if not (event := self._payload_dict.get(type)):
            event = self._payload_dict[type] = PlainEvent(f"{type.__name__}")
        return event
    
    plugin = EventProperty(PlainEvent)
    """ 任意插件 """
    
    plugin_loading = EventProperty(PlainEvent)
    """ 任意插件载入 """
    
    plugin_unloading = EventProperty(PlainEvent)
    """ 任意插件卸载 """

    @cached_property
    def _plugin_dict(self) -> dict[ModuleType, PluginSpace]:
        return {}

    def plugin_of(self, plugin: ModuleType):
        """ 特定插件 """
        if not (space := self._plugin_dict.get(plugin)):
            space = self._plugin_dict[plugin] = PluginSpace(plugin.__name__)
        return space

    meta = EventProperty(PlainEvent)
    """ 任意事件 """

    bot_init = EventProperty(PlainEvent)
    """ Bot 初始化 """

    bot_stop = EventProperty(PlainEvent)
    """ Bot 停机 """

    @cached_property
    def all_message(self):
        return MessageSpace("all")

    @cached_property
    def channel_message(self):
        return MessageSpace("channel")

    @cached_property
    def private_message(self):
        return MessageSpace("private")

    @cached_property
    def group_message(self):
        return MessageSpace("group")

    # message = EventProperty(StrEvent)
    # """ 任意消息 """
    
    # @cached_property
    # def _message_full_match_dict(self) -> dict[str, StrEvent]:
    #     return {}
    
    # def message_full_match(self, content: str):
    #     """ 消息完全匹配 """
    #     if not (event := self._message_full_match_dict.get(content)):
    #         event = self._message_full_match_dict[content] = StrEvent(f"message_full_match_{content!r}")
    #     return event
    
    # @cached_property
    # def message_regex(self) -> deque[tuple[re.Pattern, StrEvent]]:
    #     """ 消息与正则匹配 """
    #     return deque()
    
    # @cached_property
    # def message_filter_by(self) -> deque[tuple[Callable[[], bool], StrEvent]]:
    #     """ 消息与过滤函数匹配 """
    #     return deque()


class PluginSpace:

    def __init__(self, plugin_name: str):
        self.name = plugin_name

    @EventProperty[PlainEvent]
    def loading(self):
        """ 特定插件载入 """
        return PlainEvent(f"plugin_loading_{self.name}")

    @EventProperty[PlainEvent]
    def plugin_unloading(self):
        """ 特定插件卸载 """
        return PlainEvent(f"plugin_unloading_{self.name}")

class MessageSpace:

    def __init__(self, source: str):
        """ source 渠道名，如 all、group、channel """
        self.source = source
    
    @EventProperty[StrEvent]
    def any(self):
        """ 任意消息 """
        return StrEvent(f"{self.source}_message")
    
    @cached_property
    def _full_match_dict(self) -> dict[str, StrEvent]:
        return {}
    
    def full_match(self, content: str):
        """ 消息完全匹配 """
        if not (event := self._full_match_dict.get(content)):
            event = self._full_match_dict[content] = StrEvent(f"{self.source}_message_full_match_{content!r}")
        return event
    
    # @cached_property
    # def regex(self) -> deque[tuple[re.Pattern, StrEvent]]:
    #     """ 消息与正则匹配 """
    #     return deque()
    
    @EventProperty[RegexEvent]
    def regex(self):
        """ 消息与正则匹配 """
        return RegexEvent(f"{self.source}_message_regex")

    # @cached_property
    # def filter_by(self) -> deque[tuple[Callable[[], bool], StrEvent]]:
    #     """ 消息与过滤函数匹配 """
    #     return deque()

    @EventProperty[FilterByEvent]
    def filter_by(self):
        """ 消息与过滤函数匹配 """
        return FilterByEvent(f"{self.source}_message_filter_by")
