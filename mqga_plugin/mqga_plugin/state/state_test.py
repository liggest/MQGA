from mqga.plugin import plugin_info
from mqga_plugin.game_state_manager import group_game_state_manager, GameState

plugin_info(
    name="state_test",
    author="duolanda",
    version="0.0.1",
    description="测试群游戏状态"
)
from mqga import group_context as ctx, on_message
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

@on_message.regex(r"^\s*/statecheat\s*(.+)$")
async def state_cheat():
    group_state = group_game_state_manager

    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error("我不在群里，也不在频道里，那我在哪？")

    match = ctx.matched.regex
    info = match.group(1)
    if info == "show":
        return group_state.get_group_state(id).name
    elif info == GameState.LAN.name:
        group_state.update_state(id, GameState.LAN)
        return "阶段设定为局域网"
    elif info == GameState.INTERNET.name:
        group_state.update_state(id, GameState.INTERNET)
        return "阶段设定为互联网"
    elif info == GameState.FULLSPEED.name:
        group_state.update_state(id, GameState.FULLSPEED)
        return "阶段设定为通关"