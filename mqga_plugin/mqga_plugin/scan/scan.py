from mqga.plugin import plugin_info
from mqga_plugin.game_state_manager import group_game_state_manager, GameState
from mqga_plugin.lan_game_manager import LAN_game_manager

plugin_info(
    name="scan",
    author="duolanda",
    version="0.0.1",
    description="扫描局域网 ip 地址"
)
from mqga import group_context as ctx, on_message
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

@on_message.full_match(r"/scan")
async def scan():
    group_state = group_game_state_manager

    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error(f"我不在群里，也不在频道里，那我在哪？")
    
    user = message.author.id

    state = group_state.get_group_state(id)
    if state is GameState.DISCONNECTED:
        content =   '-&gt;网络数据_疑似获取_开始解析\n' \
                    '⌽⌀⌽�指令:/help\n' \
                    '开始向�␦0x1F66␦⌀�6地址中寻找⌽数据_\n' \
                    '[err␦�⌽⌽or] 0x1F66⌀⌀�6确认⌽␦�到未处理异常…\n' \
                    '写入位置0x0⌽␦␦⌀0000时发生访问�⌽�冲突…\n' \
                    '你���可以忽悠此错�⌽⌽�误并尝␦⌀␦试使用␦/help（/说明书）来���'
        return content
    else:
        game_manager = LAN_game_manager
        ips = game_manager.scan_ip(id, user)
        content = '扫描到以下ip:\n'
        for ip in ips:
            content += f"{ip}\n"
        return content
