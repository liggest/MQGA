
from pathlib import Path
from io import BytesIO
from base64 import b64decode

from httpx import AsyncClient
from anyio import Path as aPath

from mqga_plugin.static.config import StaticConfig, static

async def store(name: str, data: BytesIO | bytes):
    """ 在 data/static 以名称 name 存放文件 data  """
    config = StaticConfig.get()
    if isinstance(data, bytes):
        data = BytesIO(data)
    if not config.base_url or not config.csrf:
        path = aPath(static.data_dir / name)
        async with await path.open("wb") as f:
            await f.write(data.read())
    else:
        async with AsyncClient(base_url=config.base_url) as client:
            await client.post("/", data={"csrf": config.csrf}, files={ "files": (name, data) })
    return f"{config.base_url.rstrip('/')}/{name}"

async def store_from(path: Path, delete_this = False):
    """ 
        在 data/static 以名称 path.name 存放文件 path\n
        delete_this = True 时，在存储过后会删除文件 path 
    """
    with path.open("rb") as f:
        result = await store(path.name, f)
    if delete_this:
        path.unlink()
    return result

async def store_base64(name: str, data: str, alt_chars: str | None = None):
    """ 在 data/static 以名称 name 存放 base64 解码后的 data  """
    return await store(name, BytesIO(b64decode(data, alt_chars)))
