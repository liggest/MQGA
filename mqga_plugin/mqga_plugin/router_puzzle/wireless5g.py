""" 开启 5G，全速运行 """

from mqga_plugin.router_puzzle.game_state_manager import group_game_state_manager, GameState

from mqga import group_context as ctx, on_message
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

@on_message.regex(r"\s*/(wireless_|无线)5[gG]")
async def wireless5g():
    group_state = group_game_state_manager

    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error("我不在群里，也不在频道里，那我在哪？")

    state = group_state.get_group_state(id)

    if state is GameState.INTERNET:
        content = '原来角落中还有这个选项？！5Ghz，启动！'
        group_game_state_manager.update_state(id,GameState.FULLSPEED)
    else:
        content = '那个……现在还没有连到互联网呢'
    return content
  