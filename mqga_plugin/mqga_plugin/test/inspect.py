
from typing import TYPE_CHECKING

from textwrap import indent
import traceback

import httpx

from mqga.log import log
from mqga.lookup.context import context as ctx
from mqga.event.on import on_message
from mqga.q.message import ChannelMessage, GroupMessage

from mqga.q.constant import FileType
from mqga.q.message import IDUser
from mqga.lookup.context import BotContext
from mqga_plugin.toolz.filter import Filters
from mqga_plugin.toolz.config import SimpleConfig

import mqga_plugin.test as this_plugin
if TYPE_CHECKING:
    from mqga.plugin.module import PluginModule
    this_plugin: PluginModule


@on_message.filter_by(lambda: ctx.message.content.lower().endswith("test"))
def test():
    message = ctx.message
    source_info = ""
    if isinstance(message, ChannelMessage):
        source_info = f"{message.channel_id = }\n"
    elif isinstance(message, GroupMessage):
        source_info = f"{message.group_id = }\n"
    return f"""{message.id = }
{source_info}{message.author = }
{message.content = !r}
{message.attachments = !r}""".replace(".", "[.]")


async def reply_media_or_timeout(ctx: BotContext, url: str, content: str = "", file_type: FileType = FileType.图片):
    try:
        await ctx.bot.api.reply_media(ctx.payload, url, content=content, file_type=file_type)
    except httpx.ReadTimeout:
        await ctx.bot.api.reply_text(ctx.payload, "超时啦 > <")

# @on_message.filter_by(lambda: (ctx.matched << ctx.message.content.strip().lower()).startswith("/img"))
@on_message.filter_by(Filters.command("img", context=ctx))
@on_message.filter_by(Filters.command("image", context=ctx))
async def img():
    # cmd: str = ctx.matched.filter_by[0]
    # url = cmd.removeprefix("/img").lstrip()
    url = ctx.matched.filter_by[-1]
    # file = await ctx.bot.api.group.file(ctx.in_group.message.group_id, url)
    # log.debug(f"FileInfo: {file!r}")
    # return ctx.bot.api.group.reply_media(file, ctx.payload)
    # return ctx.bot.api.reply_media(url, ctx.payload)
    return reply_media_or_timeout(ctx, url)

@on_message.filter_by(Filters.command("audio", context=ctx))
async def audio():
    url = ctx.matched.filter_by[-1]
    return reply_media_or_timeout(ctx, url, file_type=FileType.语音)

@on_message.filter_by(Filters.command("video", context=ctx))
async def video():
    url = ctx.matched.filter_by[-1]
    return reply_media_or_timeout(ctx, url, file_type=FileType.视频)

class Config(SimpleConfig(this_plugin.data_dir / "admin.toml")):
    groups: dict[str, list[IDUser]] = {
        "12345": [IDUser(id="ABCDE")]
    }

_config = None

def _get_config():
    global _config
    if _config is None:
        _config = Config()
        _config.save()
    return _config

def is_admin():
    _config = _get_config()
    payload = ctx.payload
    source_id = ctx.bot.api.of(payload)._payload_to_id(payload)
    user_id = ctx.message.author.id
    if source_id and (users_in_source := _config.groups.get(source_id)):
        log.debug(f"{users_in_source = }")
        return any(user.id == user_id for user in users_in_source)
    return False

store = {}

@on_message.filter_by(Filters.command("py", context=ctx) & is_admin)
async def py_exec():
    script: str = ctx.matched.filter_by[-1]
    script = script.lstrip()
    if not script:
        return repr(None)
    script = f"""
async def task():
{indent(script, '    ')}
"""
    env = {
        "log": log,
        "ctx": ctx,
        "store": store 
    }
    try:
        exec(script, env)
        result = await env["task"]()
        if not isinstance(result, str):
            result = repr(result)
        return result
    except Exception as e:
        return "\n".join(traceback.format_exception(e)).replace(".", "[.]")
