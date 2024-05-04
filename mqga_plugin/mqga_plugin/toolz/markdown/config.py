from __future__ import annotations

from typing import Literal
from typing import TYPE_CHECKING

from pydantic import BaseModel, field_validator, field_serializer

from mqga import on_event, EventType, context as ctx
from mqga.log import log

if TYPE_CHECKING:
    from mqga.q.payload import EventPayload
    from mqga.q.api import MarkdownTemplate, KeyboardTemplate

from mqga_plugin.toolz.config import SimpleConfig
from mqga_plugin.toolz.markdown import by_template, keyboard

class Item(BaseModel):
    """ 配置文件中的一项 """
    name: str
    """ 模板别名 """
    id: str = ""
    """ 模板 ID """
    description: str | None = None
    """ 描述 """

    @property
    def template(self):
        raise NotImplementedError
    
    def reply_to(self, payload: EventPayload):
        raise NotImplementedError

class MarkdownItem(Item):
    """ 配置文件中的一个 markdown 模板 """

    default_params: dict[str, str | list[str]] | None = None
    """ 默认参数 """
    
    @property
    def template(self):
        # if not self.id:
        #     raise AttributeError("markdown 模板 ID 不能为空")
        return by_template(self.id, self.default_params)
    
    def with_params(self, params: dict[str, str | list[str]]):
        """ 生成带参数的 markdown 模板 """
        return by_template(self.id, {**(self.default_params or {}), **params})

    def reply_to(self, payload: EventPayload, params: dict[str, str | list[str]] | None = None, keyboard: KeyboardItem | None = None):
        if params:
            markdown: MarkdownTemplate = self.with_params(params)
        else:
            markdown: MarkdownTemplate = self.template
        if keyboard:
            keyboard: KeyboardTemplate = keyboard.template
        return ctx.bot.api.of(payload).reply_md(payload, markdown, keyboard)

class KeyboardItem(Item):
    """ 配置文件中的一个按钮模板 """

    @property
    def template(self):
        # if not self.id:
        #     raise AttributeError("按钮模板 ID 不能为空")
        return keyboard.by_template(self.id)

    def reply_to(self, payload: EventPayload, markdown: MarkdownItem | None = None):
        if markdown:
            markdown: MarkdownTemplate = markdown.template
        return ctx.bot.api.of(payload).reply_md(payload, markdown, self.template)

class Config(SimpleConfig("markdown.toml")):
    markdown: dict[str, MarkdownItem] | None = None
    keyboard: dict[str, KeyboardItem] | None = None

    @field_validator("markdown", "keyboard", mode="before")
    @classmethod
    def list2dict(cls, v: list[dict] | None):
        log.debug(repr(v))
        if v is not None:
            return { item["name"]: item for item in v }
        
    @field_serializer("markdown", "keyboard")
    @classmethod
    def dict2list(cls, v: dict[str, Item] | None):
        if v is not None:
            return [*v.values()]

    def register(self, map_name: Literal["markdown", "keyboard"], name: str, description: str | None = None, **kw):
        _map: dict[str, Item] | None = getattr(self, map_name)
        if _map is None:
            _map = {}
            setattr(self, map_name, _map)

        if map_name == "markdown":
            hint = "markdown 模板"
            ItemCls = MarkdownItem
        elif map_name == "keyboard":
            hint = "按钮模板"
            ItemCls = KeyboardItem

        if item := _map.get(name):
            log.debug(f"已从配置中加载 {hint} {item!r}")
        else:
            item = ItemCls(name=name, description=description, **kw)
        if not item.id:
            log.warning(f"{hint} {item!r} 尚未配置 ID")
        _map[name] = item
        return item

def register_markdown(name: str, description: str | None = None, default_params: dict[str, str] | None = None) -> MarkdownItem:
    """ 注册一个 markdown 模板到配置文件 """
    return Config.get().register("markdown", name, description, default_params=default_params)

def register_keyboard(name: str, description: str | None = None) -> KeyboardItem:
    """ 注册一个按钮模板到配置文件 """
    return Config.get().register("keyboard", name, description)

@on_event.of(EventType.WSReady)
def _ready():
    if Config.is_init():
        Config.get().save()  # 加载完成时更新配置文件
