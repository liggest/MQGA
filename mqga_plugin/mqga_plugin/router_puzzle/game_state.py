""" 返回游戏的状态 """

from mqga_plugin.router_puzzle.game_state_manager import group_game_state_manager, GameState

from mqga import group_context as ctx, on_message
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

@on_message.full_match(r"/状态")
@on_message.full_match(r"/state")
async def game_state():
    group_state = group_game_state_manager

    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error("我不在群里，也不在频道里，那我在哪？")

    state = group_state.get_group_state(id)
    log.info("我看看怎么个事")
    log.info(state)
    if state is GameState.DISCONNECTED:
        content =   '路由器状态如下:\n' \
                    'CPU	5%\n' \
                    '内存	2MB/128MB\n' \
                    '上传	0KB/s\n' \
                    '下载	0KB/s\n' \
                    '温度	18℃\n' \
                    '2.4GHz	off\n' \
                    '5Ghz	off\n' \
                    '局域网状态	未连接\n' \
                    '互联网状态	未连接'
        return content
    elif state is GameState.LAN:
        content =   '路由器状态如下:\n' \
                    'CPU	10%\n' \
                    '内存	27MB/128MB\n' \
                    '上传	20KB/s\n' \
                    '下载	10KB/s\n' \
                    '温度	20℃\n' \
                    '2.4GHz	off\n' \
                    '5Ghz	off\n' \
                    '局域网状态	已连接\n' \
                    '互联网状态	未连接'
        return content
    elif state is GameState.INTERNET:
        content =   '路由器状态如下:\n' \
                    'CPU	20%\n' \
                    '内存	32MB/128MB\n' \
                    '上传	5MB/s\n' \
                    '下载	4MB/s\n' \
                    '温度	30℃\n' \
                    '2.4GHz	on\n' \
                    '5Ghz	off\n' \
                    '局域网状态	已连接\n' \
                    '互联网状态	已连接'
        return content
    elif state is GameState.FULLSPEED:
        content =   '路由器状态如下:\n' \
                    'CPU	39%\n' \
                    '内存	54MB/128MB\n' \
                    '上传	20MB/s\n' \
                    '下载	10MB/s\n' \
                    '温度	60℃\n' \
                    '2.4GHz	on\n' \
                    '5Ghz	on\n' \
                    '局域网状态	已连接\n' \
                    '互联网状态	已连接'
        return content
    else:
        return "你来到了荒漠"
