from typing import TypedDict, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import NotRequired

    class SessionStartLimit(TypedDict):
        """ 当前的 session 启动限制 """
        total: int
        """ 每 24 小时可创建 Session 数 """
        remaining: int
        """ 目前还可以创建的 Session 数 """
        reset_after: int
        """ 重置计数的剩余时间（毫秒） """
        max_concurrency: int
        """ 每 5 秒可以创建的 Session 数 """

    class WSURL(TypedDict):
        url: str
        """ ws 连接地址 """
        shards: NotRequired[int]
        """ 建议的 shard 数 """
        session_start_limit: NotRequired[SessionStartLimit]

    class AccessToken(TypedDict):
        access_token: str
        expires_in: str

    class RepliedMessage(TypedDict):
        id: str
        """ 消息 id """
        timestamp: int

    class FileInfo(TypedDict):
        file_uuid: str
        """ 文件 id """
        file_info: str
        """ 文件信息 """
        ttl: int
        """ 有效期，为 0 时一直有效 """

    class MarkdownParam(TypedDict):
        key: str
        """ 参数名 """
        values: list[str]
        """ 参数值 """

    class MarkdownTemplate(TypedDict):
        """ markdown 模板 """
        custom_template_id: str
        """ 模板 ID """
        params: NotRequired[list[MarkdownParam]]
        """ 模板内含的动态参数 """

    class MarkdownCustom(TypedDict):
        """ 原生 markdown """
        content: str
        """ 内容 """

    # class ChannelMarkdown(TypedDict):
    #     template_id: int
    #     """ 模板 id """
    #     params: list[MarkdownParam]
    #     """ 模板内含的动态参数 """

    class KeyboardTemplate(TypedDict):
        """ 按钮模板 """
        id: str
        """ 模板 ID """

    from mqga.q.constant import ButtonStyle, ButtonPermissionType, ButtonActionType

    class ButtonRenderData(TypedDict):
        """ 按钮外观 """
        label: str
        """ 常态文本 """
        visited_label: str
        """ 按下后文本 """
        style: ButtonStyle
        """ 按钮样式 """

    class ButtonPermission(TypedDict):
        """ 按钮权限 """
        type: ButtonPermissionType
        """ 权限类型 """

    class ButtonPermissionForUser(ButtonPermission):
        """ 指定用户的按钮权限 """
        type: Literal[ButtonPermissionType.指定用户]
        """ 权限类型 """
        specify_user_ids: list[str]
        """ 指定用户 ID 列表 """

    from mqga.q.constant import RoleID

    class ButtonPermissionForRole(ButtonPermission):
        """ 指定身份组的按钮权限 """
        type: Literal[ButtonPermissionType.指定身份组]
        """ 权限类型 """
        specify_role_ids: list[RoleID | str]
        """ 指定身份组 ID 列表 """

    class ButtonAction(TypedDict):
        """ 按钮动作 """
        type: ButtonActionType
        """ 动作类型 """
        permission: ButtonPermissionForUser | ButtonPermissionForRole | ButtonPermission
        """ 动作权限 """
        data: str
        """ 动作附带数据 """
        unsupport_tips: str
        """ 动作不支持时的提示 """

    class CommandButtonAction(ButtonAction):
        """ 指令按钮动作 """
        type: Literal[ButtonActionType.指令]
        """ 动作类型 """
        data: str
        """ 要为交互者自动输入的指令 """
        reply: NotRequired[bool]
        """ 是否回复当前按钮消息，默认为 `False` """
        enter: NotRequired[bool]
        """ 是否自动发送指令，默认为 `False` """
        anchor: NotRequired[int]
        """ 为 `1` 时，忽略 `enter` 的效果，按下按钮会唤起手机 QQ 选图器 """  # ？

    class JumpButtonAction(ButtonAction):
        """ 跳转按钮动作 """
        type: Literal[ButtonActionType.跳转]
        """ 动作类型 """
        data: str
        """ 跳转链接等 """

    class InteractButtonAction(ButtonAction):
        """ 回调按钮动作 """
        type: Literal[ButtonActionType.回调]
        """ 动作类型 """
        data: str
        """ 回调数据 """

    class Button(TypedDict):
        """ 按钮 """
        id: NotRequired[str]
        """ 按钮 ID，应在按钮面板中取唯一值 """
        render_data: ButtonRenderData
        """ 外观数据 """
        action: JumpButtonAction | InteractButtonAction | CommandButtonAction | ButtonAction
        """ 动作 """

    class KeyboardRow(TypedDict):
        """ 一行按钮 """
        buttons: list[Button]

    class KeyboardContent(TypedDict):
        """ 自定义按钮的内容 """
        rows: list[KeyboardRow]
        """ 按钮行 """

    class KeyboardCustom(TypedDict):
        """ 自定义按钮 """
        content: KeyboardContent
        """ 内容 """
