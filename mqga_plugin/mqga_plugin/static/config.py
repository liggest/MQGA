
from typing import TYPE_CHECKING

from mqga import on_event, EventType
from mqga_plugin.toolz import SimpleConfig

import mqga_plugin.static as static

if TYPE_CHECKING:
    from mqga.plugin.module import PluginModule
    static: PluginModule

class StaticConfig(SimpleConfig("static.toml")):
    base_url: str = "http://127.0.0.1:8000/"
    csrf: str = ""

@on_event.of(EventType.WSReady)
def _ready():
    config = StaticConfig.get()  # 加载完成时更新配置文件
    config.save()
    if config.base_url and config.csrf:  # 不是本地的 data/static
        return
    index = static.data_dir / "index.html"  # 也保证了 data_dir 存在
    if not index.exists():
        with index.open("w", encoding="utf-8") as f:
            f.writelines([
                "<!DOCTYPE html>",
                "<html>",
                '  <head><meta charset="utf-8"></head>',
                "  <body>",
                "    <h1>四零四。</h1>",
                '    <input type="hidden" name="csrf" value="0pR&fwRQE">'  # :)
                "  </body>",
                "</html>"
            ])
