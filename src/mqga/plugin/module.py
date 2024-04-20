import sys
import types
import inspect
from pathlib import Path
from functools import cached_property

from mqga.log import log

class PluginModuleMeta(type):

    def __del__(self):
        log.debug(f"PluginModuleMeta.__del__  {self!r} 使命结束")

class PluginModule(types.ModuleType, metaclass=PluginModuleMeta):
    
    name = "plugin"
    """ 插件名称 """

    author = ""
    """ 插件作者 """

    version = "0.0.1"
    """ 插件版本 """
    
    description = "一般 MQGA 插件"
    """ 插件简介 """

    def __repr__(self):
        return f"<PluginModule {self.name!r}>"
    
    def __dir__(self):  # 为 dir(PluginModule()) 补充 name、path 等来自 PluginModule 的项
        return [*super().__dir__(), *(name for name in dir(self.__class__) if not name.startswith("_"))]

    def __del__(self):
        log.debug(f"PluginModule.__del__  {self!r} 使命结束")

    @cached_property  # 在 loader 里会被赋值，对于单文件，为文件路径，对于目录，为目录路径
    def path(self):
        """ 插件路径 """
        return Path(self.__file__) if not self.__file__.endswith("__init__.py") else Path(self.__file__).parent

    @cached_property
    def data_dir(self):
        """ 插件数据目录 """
        path = Path(f"./data/{self.path.stem}")
        path.mkdir(parents=True, exist_ok=True)
        log.debug(f"确保插件 {self.name} 的数据目录 {path.as_posix()} 存在")
        return path
    
def plugin_info(name="", author="", version="0.0.1", description="一般 MQGA 插件") -> type[PluginModule]:
    """ 设置插件信息 """
    frame = inspect.currentframe() # 找到调用函数所在的模块
    while not frame.f_code.co_name == "<module>":
        frame = frame.f_back
    path = Path(frame.f_code.co_filename)
    while (parent_name := path.parent.name) and parent_name != "mqga_plugin":
        # path 为 "/" 或 "." 时 path.name = ""，防止死循环
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

    cls = sys.modules[module_name].__class__ = types.new_class(class_name, (PluginModule,), exec_body=class_body)
    return cls

def _to_plugin_module(module: types.ModuleType, path: Path) -> PluginModule:
    """ 将 module 转换为默认名称的插件模块 """
    name = path.name.removesuffix(".py")
    class_name = f"{name.capitalize()}PluginModule"

    def class_body(namespace: dict):
        namespace["name"] = name

    module.__class__ = types.new_class(class_name, (PluginModule,), exec_body=class_body)
    return module
