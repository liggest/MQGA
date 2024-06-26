
from mqga import on_message, context as ctx
from mqga.plugin.module import PluginModule
from mqga.log import log

from mqga_plugin.toolz import Filters

from mqga.plugin import plugin_info
plugin_info("service", description="服务列表（")

@on_message.filter_by(Filters.prefix("/服务列表"))
def service():
    return """--------服务列表--------
发送"/用法 name"查看详情

1: ●autowithdraw
2: ●manager
3: ●score
4: ●ygocdb
5: ●mcfish
6: ●cybercat
7: ●emojimix
8: ●fortune
9: ●runcode
10: ●wife
11: ●wordle
12: ○qunyou"""

def plugin_list():
    yield "插件列表"
    for name, plugin in ctx.bot._plugins.items():
        name = name.replace('.', '_')
        assert isinstance(plugin, PluginModule)
        if hasattr(plugin, "name"):
            description = f"\t{plugin.description}" if plugin.description != PluginModule.description else ""
            yield f"{plugin.name}({name}){description}"
        else:
            yield name

@on_message.filter_by(Filters.command("/插件列表测试"))
def plugin_test():
    log.debug(ctx.matched.filter_by)
    return "\n".join(plugin_list())
