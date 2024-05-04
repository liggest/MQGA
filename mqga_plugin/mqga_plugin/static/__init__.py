
from mqga.plugin import plugin_info

plugin_info("static", description="只是换个文件夹存放一些文件而已（")

from mqga_plugin.static import config
from mqga_plugin.static.store import store, store_from, store_base64

__all__ = ["config", "store", "store_from", "store_base64"]
