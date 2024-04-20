
from mqga.plugin import plugin_info

plugin_info("toolz", "liggest", description="MQGA 工具集")

from mqga_plugin.toolz.filter import Filters
from mqga_plugin.toolz.config import SimpleConfig

__all__ = ["Filters", "SimpleConfig"]
