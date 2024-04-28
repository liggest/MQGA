
import re

from mqga import on_message, context as ctx
from mqga.log import log
from mqga.connection.api.client import APIError
from mqga.q.payload import ButtonInteractEventPayload

from mqga_plugin.toolz import Filters
from mqga_plugin.toolz.markdown import register_markdown, keyboard
from mqga_plugin.toolz.markdown.keyboard import JumpButton, CommandButton, InteractButton

md_test = register_markdown("测试模板", "测试用的模板", {"md7": "**", "md8": "你好，世界", "md9": "**"})

split_ptn = re.compile(r"\*+|_+|#+|~+|\]\(|\d\.|-|>|`|//")

def split_md(content: str):
    content = content.replace("\n", "\r")
    idx = 0
    current = ""
    for match in split_ptn.finditer(content):
        e = match.end()
        current += content[idx:e]
        idx = e
        yield current
        current = ""
    
    if idx < len(content):
        current += content[idx:]
        yield current

async def report_api_error(coro):
    try:
        return await coro
    except APIError as e:
        log.exception("", exc_info=e)
        return await ctx.bot.api.reply_text(ctx.payload, repr(e))

@on_message.filter_by(Filters.command("md", context=ctx))
async def md():
    md_content: str = ctx.matched.filter_by[-1]
    params = {f"md{i}": part for i, part in enumerate(split_md(md_content))}
    return report_api_error(md_test.reply_to(ctx.payload, params))


b1 = JumpButton("MQGA!", "https://github.com/liggest/MQGA")
b1.style = keyboard.ButtonStyle.Blue
b1.pressed_text = "GAMQ!"

b2 = CommandButton("解码语者", "image https://cdn.233.momobako.com/ygopro/pics/1861629.jpg")
b2.is_enter = True
b2.is_reply = True
b2.permission_type = keyboard.ButtonPermissionType.管理员

b3 = InteractButton("戳", "xyz", "嗷~")
@b3.on_interact
async def on_interact():
    # log.warning(repr(ctx.payload.data))
    payload: ButtonInteractEventPayload = ctx.payload
    await ctx.bot.api.reply_text(payload, payload.data.button.data)
    return keyboard.InteractionResult.操作成功

b4 = CommandButton("这是指令", "image https://cdn.233.momobako.com/ygopro/pics/1861629.jpg")
b4.pressed_text = "按下去了！"
b4.is_enter = True

b5 = JumpButton("这是链接", "https://github.com/liggest/MQGA")
b5.pressed_text = "按下去了！"

@on_message.filter_by(Filters.command("key", context=ctx))
async def key():
    md_content: str = ctx.matched.filter_by[-1]
    params = {f"md{i}": part for i, part in enumerate(split_md(md_content))}
    return report_api_error(
        ctx.bot.api.reply_md(ctx.payload, md_test.with_params(params), keyboard.by_buttons([b1, b2], [b3]))
    )
    # return ctx.bot.api.reply_md(ctx.payload, md_test.with_params(params), keyboard.by_buttons([b4, b5]))
