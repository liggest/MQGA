
from typing import TYPE_CHECKING
import asyncio
import typst
# from datetime import datetime
from tempfile import NamedTemporaryFile

from mqga import on_message, context as ctx, log
from mqga_plugin.toolz.filter import Filters
# from mqga_plugin.static import store
from mqga_plugin.test.inspect import reply_media_or_timeout

import mqga_plugin.typst as plugin

if TYPE_CHECKING:
    from mqga.plugin.module import PluginModule
    plugin: PluginModule

@on_message.filter_by(Filters.command("typ", ignore_case=True, context=ctx))
async def typ(content = "", args: dict[str, str] = None):
    content = content or "".join(ctx.matched.filter_by)
    try:
        out = await asyncio.to_thread(render_typ, content, args)
    except RuntimeError as e:
        return "".join(e.args).replace(".", "[.]")
    # url = await store(f"render_typ_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", out)
    # log.debug(f"渲染得到的链接：{url}")
    # await image(url)
    log.debug(f"渲染得到图片大小：{len(out)} bytes")
    await reply_media_or_timeout(ctx, out)
    

def render_typ(content: str, args: dict[str, str] = None):
    with NamedTemporaryFile(suffix=".typ", dir=plugin.data_dir.as_posix()) as f:
        f.write("#set page(width: auto, height: auto, margin: 4pt)\n".encode("utf-8"))
        f.write(content.encode("utf-8"))
        f.flush()
        file_path = plugin.data_dir / f.name
        return typst.compile(file_path, output=None, format="png", sys_inputs=args or {})
