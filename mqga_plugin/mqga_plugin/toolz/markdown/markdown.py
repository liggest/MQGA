""" markdown 相关 """

from __future__ import annotations

from typing import TYPE_CHECKING

from urllib.parse import quote

if TYPE_CHECKING:
    from mqga.q.api import MarkdownTemplate, MarkdownCustom

def by_content(content: str) -> MarkdownCustom:
    """ 原生 markdown """
    return { "content": content }

def by_template(id: str, params: dict[str, str | list[str]] | None = None) -> MarkdownTemplate:
    """ markdown 模板 """
    md: MarkdownTemplate = { "custom_template_id": id }
    if params:
        md["params"] = [
            {"key": k, "values": [v] if isinstance(v, str) else [*v]} 
            for k, v in params.items()
        ]
    return md

class Snippet:
    """ QQ markdown 文本交互快捷片段 """

    @staticmethod
    def at(user_id: str):
        """ @user_id """
        return f"<@{user_id}>"
    
    @staticmethod
    def at_all():
        """ @全体成员 """
        return "@everyone"

    @staticmethod
    def inline_command(text: str, command: str, enter = False, reply = False):  # 也编码 "/"
        """ MD 文本指令 """
        return f"[{text}](mqqapi://aio/inlinecmd?command={quote(command, safe='')}&reply={str(reply).lower()}&enter={str(enter).lower()})"

    @staticmethod
    def to_channel(channel_id: str):
        """ 跳转到 channel_id 对应的子频道 """
        return f"<#{channel_id}>"
    
    @staticmethod
    def emoji(emoji_id: str):
        """ emoji_id 对应的系统表情 """
        return f"<emoji:{emoji_id}>"
