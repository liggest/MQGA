from __future__ import annotations

from functools import cached_property
from types import ModuleType
from collections import deque
import re

from typing import Callable

from mqga.event.event import PlainEvent, StrEvent
from mqga.q.payload import Payload
from mqga.q.message import Message

class Space:

    @cached_property
    def payload(self):
        """ 任意 Payload """
        return PlainEvent("payload")
    
    @cached_property
    def _payload_dict(self) -> dict[type[Payload], PlainEvent]:
        return {}
    
    def payload_of(self, type: type[Payload]):
        """ 特定 Payload """
        if not (event := self._payload_dict.get(type)):
            event = self._payload_dict[type] = PlainEvent(f"{type.__name__}")
        return event

    @cached_property
    def plugin(self):
        """ 任意插件 """
        return PlainEvent("plugin")
    
    @cached_property
    def plugin_loading(self):
        """ 任意插件载入 """
        return PlainEvent("plugin_loading")
    
    @cached_property
    def plugin_unloading(self):
        """ 任意插件卸载 """
        return PlainEvent("plugin_unloading")

    @cached_property
    def _plugin_dict(self) -> dict[ModuleType, PluginSpace]:
        return {}

    def plugin_of(self, plugin: ModuleType):
        """ 特定插件 """
        if not (space := self._plugin_dict.get(plugin)):
            space = self._plugin_dict[plugin] = PluginSpace(plugin.__name__)
        return space

    @cached_property
    def meta(self):
        """ 任意事件 """
        return PlainEvent("meta")

    @cached_property
    def bot_init(self):
        """ Bot 初始化 """
        return PlainEvent("bot_init")

    @cached_property
    def bot_stop(self):
        """ Bot 停机 """
        return PlainEvent("bot_stop")

    @cached_property
    def message(self):
        """ 任意消息 """
        return StrEvent("message")
    
    @cached_property
    def _message_full_match_dict(self) -> dict[str, StrEvent]:
        return {}
    
    def message_full_match(self, content: str):
        """ 消息完全匹配 """
        if not (event := self._message_full_match_dict.get(content)):
            event = self._message_full_match_dict[content] = StrEvent(f"message_full_match_{content!r}")
        return event
    
    @cached_property
    def message_regex(self) -> deque[tuple[re.Pattern, StrEvent]]:
        """ 消息与正则匹配 """
        return deque()
    
    @cached_property
    def message_filter_by(self) -> deque[tuple[Callable[[Message], bool], StrEvent]]:
        """ 消息与过滤函数匹配 """
        return deque()


class PluginSpace:

    def __init__(self, plugin_name: str):
        self.name = plugin_name

    @cached_property
    def loading(self):
        """ 特定插件载入 """
        return PlainEvent(f"plugin_loading_{self.name}")

    @cached_property
    def plugin_unloading(self):
        """ 特定插件卸载 """
        return PlainEvent(f"plugin_unloading_{self.name}")
