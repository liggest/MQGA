""" ping ip 地址取得不同效果 """

from mqga_plugin.router_puzzle.game_state_manager import group_game_state_manager, GameState
from mqga_plugin.router_puzzle.lan_game_manager import LAN_game_manager

from mqga import group_context as ctx, on_message
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

@on_message.regex(r"^\s*/探测\s*(.*)$")
@on_message.regex(r"^\s*/ping\s*(.*)$")
async def ping():
    group_state = group_game_state_manager
    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error("我不在群里，也不在频道里，那我在哪？")
    state = group_state.get_group_state(id)
    user = message.author.id

    match = ctx.matched.regex
    info = match.group(1)
    # log.info("让我康康")
    # log.info(info)
    if state is GameState.DISCONNECTED:
        content =   '-&gt;网络数据_疑似获取_开始解析\n' \
                    '⌽⌀⌽�指令:/help\n' \
                    '开始向�␦0x1F66␦⌀�6地址中寻找⌽数据_\n' \
                    '[err␦�⌽⌽or] 0x1F66⌀⌀�6确认⌽␦�到未处理异常…\n' \
                    '写入位置0x0⌽␦␦⌀0000时发生访问�⌽�冲突…\n' \
                    '你���可以忽悠此错�⌽⌽�误并尝␦⌀␦试使用␦/help（/说明书）来���'
        return content
    elif not info:
        return "请提供要探测的 ip 地址"
    else:
        game_manager = LAN_game_manager
        content = game_manager.ping_ip(id, user, info)
        return content
