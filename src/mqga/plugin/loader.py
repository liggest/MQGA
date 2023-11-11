from types import ModuleType
import importlib
# from importlib.util import spec_from_file_location, module_from_spec
import sys
from pathlib import Path

from mqga.log import log

def load(root = Path("./plugin")) -> dict[Path, ModuleType]:
    root_str = root.as_posix()
    sys.path.insert(0, root_str)
    log.info(f"从 {root_str} 中载入插件…")
    plugins = {}
    for path in root.iterdir():
        if path.name.startswith("_"):
            continue
        if path.suffix.endswith(".py") or (path.is_dir() and (path / "__init__.py").exists()):
            try:
                plugins[path] = load_one(path)
                log.info(f"{path.as_posix()} 加载成功~")
            except Exception as e:
                log.exception(f"{path.as_posix()} 加载失败！", exc_info=e)
    if sys.path and sys.path[0] is root_str:
        sys.path.pop(0)
        
def load_one(path: Path) -> ModuleType:
    # spec = spec_from_file_location(path.stem, path)
    # module = module_from_spec(spec)
    # spec.loader.exec_module(module)
    return importlib.import_module(path.stem)
