
from mqga.plugin import plugin_info

plugin_info("typst", author="liggest", description="渲染 typst 格式的输入到图片！")

from mqga_plugin.typst import typ

__all__ = ["typ"]
