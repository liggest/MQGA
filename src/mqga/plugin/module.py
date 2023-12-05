import sys
import types
import inspect
from pathlib import Path

class PluginModule(types.ModuleType):
    
    name = "plugin"
    """ 插件名称 """

    author = ""
    """ 插件作者 """

    version = ""
    """ 插件版本 """
    
    description = "一般 MQGA 插件"
    """ 插件简介 """

    def __repr__(self):
        return f"<PluginModule {self.name!r}>"

def plugin_info(name="", author="", version="0.0.1", description="一般 MQGA 插件"):
    """ 设置插件信息 """
    # 找到调用函数所在的模块
    frame = inspect.currentframe()
    while not frame.f_code.co_qualname == "<module>":
        frame = frame.f_back
    path = Path(frame.f_code.co_filename)
    while path.parent.name != "mqga_plugin":
        path = path.parent
    file_name = path.name.removesuffix(".py")
    name = name or file_name  # 没有名字的话用文件名
    module_name = f"mqga_plugin.{file_name}"
    class_name = f"{file_name.capitalize()}PluginModule"

    def class_body(namespace: dict):
        namespace["name"] = name
        namespace["author"] = author
        namespace["version"] = version
        namespace["description"] = description

    cls = sys.modules[module_name].__class__ = types.new_class(class_name, (PluginModule,), {}, class_body)
    return cls