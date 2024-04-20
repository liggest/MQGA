""" markdown 相关 """

from __future__ import annotations

from typing import TYPE_CHECKING

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
