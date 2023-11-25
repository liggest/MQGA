from types import ModuleType
import importlib
# from importlib.util import spec_from_file_location, module_from_spec
import sys
from pathlib import Path

from mqga.log import log

def load(root = Path("./mqga_plugin/mqga_plugin")) -> dict[Path, ModuleType]:
    # if not (root / "__init__.py").exists():
    #     raise ValueError(f"请在 {root!r} 中创建 __init__.py，使其变成一个 Python 包")
    parent = root.parent
    parent_abs = parent.as_posix()
    sys.path.insert(0, parent_abs)
    log.info(f"从 {root.as_posix()} 中载入插件…")
    plugins = {}
    for path in root.iterdir():
        if path.name.startswith("_"):
            continue
        if path.suffix.endswith(".py") or (path.is_dir() and (path / "__init__.py").exists()):
            try:
                plugins[path] = load_one(root, path)
                log.info(f"插件 {path.as_posix()} 加载成功~")
            except Exception as e:
                log.exception(f"插件 {path.as_posix()} 加载失败！", exc_info=e)
    if sys.path and sys.path[0] is parent_abs:
        sys.path.pop(0)
        
def load_one(root: Path, path: Path) -> ModuleType:
    # spec = spec_from_file_location(path.stem, path)
    # module = module_from_spec(spec)
    # spec.loader.exec_module(module)
    return importlib.import_module(f"{root.stem}.{path.stem}")
