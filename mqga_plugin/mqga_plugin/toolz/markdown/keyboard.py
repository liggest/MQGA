""" 按钮相关 """

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Callable
from collections import deque

if TYPE_CHECKING:
    from mqga.q.api import KeyboardTemplate, KeyboardCustom
    from mqga.q.api import Button as ButtonData
    from mqga.q.api import ButtonPermissionForRole, ButtonPermissionForUser

from mqga.log import log
from mqga.q.constant import ButtonStyle, ButtonActionType, ButtonPermissionType, InteractionResult
from mqga import on_event, EventType, context as ctx
from mqga.event.box import Box
from mqga.event.event import PlainReturns
from mqga.q.payload import ButtonInteractEventPayload

def by_template(id: str) -> KeyboardTemplate:
    """ 按钮模板 """
    return { "id": id }

# from typing import Callable
# def inner_property(root: Callable[[Button], dict], name: str, doc: str = ""):
#     def _get(self):
#         return root(self)[name]
#     def _set(self, value):
#         root(self)[name] = value
#     return property(_get, _set, doc=doc)

class Button:
    """ 按钮 """
    
    @property
    def _appearance(self):
        return self._data["render_data"]
    
    @property
    def text(self):
        """ 文本 """
        return self._appearance["label"]
    
    @text.setter
    def text(self, value: str):
        self._appearance["label"] = value
    
    @property
    def pressed_text(self):
        """ 按下后文本 """
        return self._appearance["visited_label"]

    @pressed_text.setter
    def pressed_text(self, value: str):
        self._appearance["visited_label"] = value
    
    @property
    def style(self):
        """ 样式 """
        return self._appearance["style"]
    
    @style.setter
    def style(self, value: ButtonStyle):
        self._appearance["style"] = value
    
    @property
    def _action(self):
        return self._data["action"]
    
    @property
    def type(self):
        """ 类型 """
        return self._action["type"]
    
    @type.setter
    def type(self, value: ButtonActionType):
        self._action["type"] = value
    
    @property
    def _action_data(self):
        return self._action["data"]
    
    @_action_data.setter
    def _action_data(self, value: str):
        self._action["data"] = value

    @property
    def _permission(self):
        return self._action["permission"]

    @property
    def permission_type(self):
        """ 权限类型 """
        return self._permission["type"]
    
    @permission_type.setter
    def permission_type(self, value: ButtonPermissionType):
        self._permission["type"] = value

    @property
    def permission_list(self):
        """ 权限 ID 列表 """
        match self.permission_type:
            case ButtonPermissionType.指定用户:
                if TYPE_CHECKING:
                    assert isinstance(self._permission, ButtonPermissionForUser)
                return self._permission.get("specify_user_ids")
            case ButtonPermissionType.指定身份组:
                if TYPE_CHECKING:
                    assert isinstance(self._permission, ButtonPermissionForRole) 
                return self._permission.get("specify_role_ids")

    @permission_list.setter
    def permission_list(self, value: list[str]):
        match self.permission_type:
            case ButtonPermissionType.指定用户:
                self._permission["specify_user_ids"] = value
            case ButtonPermissionType.指定身份组:
                self._permission["specify_role_ids"] = value
            case _:
                log.warning(f"权限类型为 {self.permission_type!r} 的按钮 {self!r} 不支持指定权限 ID 列表")

    @property
    def unsupport_tips(self):
        """ 不可用提示 """
        return self._action["unsupport_tips"]
    
    @unsupport_tips.setter
    def unsupport_tips(self, value: str):
        self._action["unsupport_tips"] = value

    @property
    def id(self):
        """ 按钮 ID """
        return self._data.get("id", "")
    
    @id.setter
    def id(self, value: str):
        self._data["id"] = value

    def __init__(self, text: str, type: ButtonActionType, data: str = ""):
        self._data: ButtonData = {
            "render_data": {
                "label": text,
                "visited_label": text,
                "style": ButtonStyle.Gray
            },
            "action" : {
                "type": type,
                "data": data,
                "permission": {
                    "type": ButtonPermissionType.所有人
                },
                "unsupport_tips": "按钮尚不可用",
            }
        }

    def __repr__(self):
        return f"{self.__class__.__name__}({self.text!r}, {self.type!r}, {self._action_data!r})"

class JumpButton(Button):
    """ 跳转按钮 """

    @property
    def target(self):
        """ 跳转链接等 """
        return self._action_data
    
    @target.setter
    def target(self, value: str):
        self._action_data = value

    def __init__(self, text: str, target: str):
        super().__init__(text, ButtonActionType.跳转, target)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.text!r}, {self.target!r})"

# ButtonEvent = MultiEvent[[], InteractionResult | PlainReturns]
# TODO Button 事件

# _callbacks: dict[str, ButtonEvent] | None = None

# async def _with_callbacks():
#     payload: ButtonInteractEventPayload = ctx.payload
#     if _callbacks:
#         if event := _callbacks.get(payload.data.data.button.id):
#             await event.emit()

class InteractButton(Button):
    """ 回调按钮 """

    @property
    def data(self):
        """ 回调数据 """
        return self._action_data
    
    @data.setter
    def data(self, value: str):
        self._action_data = value

    @property
    def _boxes(self):
        if self._boxes_ is None:
            self._boxes_ = deque()
        return self._boxes_

    def __init__(self, text: str, id: str, data: str):
        super().__init__(text, ButtonActionType.回调, data)
        self._data["id"] = id
        self._boxes_ = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.text!r}, {self.data!r})"

    # def __del__(self):
    #     试着在按钮被移除时也取消它注册的回调
    #     if self._boxes_ and _callbacks:
    #         if event := _callbacks.get(self.id):
    #             for box in self._boxes_:
    #                 event.unregister(box)

    def on_interact(self, func: Callable[[], InteractionResult | PlainReturns]):
        box = Box(func)
        @on_event.of(EventType.ButtonInteract)
        async def inner():
            payload: ButtonInteractEventPayload = ctx.payload
            if payload.data.data.button.id == self.id:
                return await box()
        # self._boxes.append(inner)
        # global _callbacks
        # if _callbacks is None:
        #     _callbacks = {}
        #     on_event.of(EventType.ButtonInteract)(_with_callbacks)
        # _id = self.id
        # if not (event := _callbacks.get(_id)):
        #     event = _callbacks[_id] = ButtonEvent(f"button_interact_{_id!r}")
        # box = Box(func)
        # self._boxes.append(box)
        # event.register(box)
        return func

class CommandButton(Button):
    """ 指令按钮 """

    @property
    def command(self):
        """ 指令 """
        return self._action_data
    
    @command.setter
    def command(self, value: str):
        self._action_data = value

    @property
    def is_enter(self) -> bool:
        """ 自动发送指令 """
        return self._action.get("enter", False)
    
    @is_enter.setter
    def is_enter(self, value: bool):
        self._action["enter"] = value

    @property
    def is_reply(self):
        """ 回复当前按钮消息 """
        return self._action.get("reply", False)
    
    @is_reply.setter
    def is_reply(self, value: bool):
        self._action["reply"] = value

    @property
    def is_photo_picker(self):
        """ 唤起手机 QQ 选图器 """
        return self._action.get("anchor") == 1
    
    @is_photo_picker.setter
    def is_photo_picker(self, value: bool):
        self._action["anchor"] = 1 if value else 0

    def __init__(self, text: str, command: str):
        super().__init__(text, ButtonActionType.指令, command)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.text!r}, {self.command!r})"


def by_buttons(*rows: Iterable[Button]) -> KeyboardCustom:
    """ 自定义按钮 """
    return { 
        "content": {
            "rows": [
                { "buttons": [ button._data for button in buttons ] }
                for buttons in rows
            ]
        }
    }
