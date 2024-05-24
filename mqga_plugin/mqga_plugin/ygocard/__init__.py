
from mqga.plugin import plugin_info

plugin_info("YGO卡查", author="liggest", description="通过百鸽等渠道提供游戏王查卡功能")

from mqga_plugin.ygocard import baige, baige2

__all__ = ["baige", "baige2"]
