
from mqga.lookup.context import group_context as ctx
from mqga.event.on import on_group_message as on_msg


@on_msg.filter_by(lambda: ctx.message.content.lower().endswith("test"))
def test():
    message = ctx.message
    return f"""{message.id = }
{message.group_id = }
{message.author = }
{message.content = !r}
{message.attachments = !r}"""

@on_msg.filter_by(lambda: ctx.message.content.lower().endswith("wait"))
def wait():
    bot = ctx.bot
    payload = ctx.payload
    import asyncio
    async def delay(seconds = 3):
        await asyncio.sleep(seconds)
        await bot._api.group_reply(str(seconds), payload)
    return delay()
