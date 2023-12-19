from mqga.plugin import plugin_info
from mqga_plugin.game_state_manager import group_game_state_manager, GameState

plugin_info(
    name="plug",
    author="duolanda",
    version="0.0.1",
    description="插网线，推进游戏进程",
)
from mqga import group_context as ctx, on_message
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log

@on_message.full_match(r"/插网线")
@on_message.full_match(r"/plug")
async def plug_show():
    group_state = group_game_state_manager
    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error("我不在群里，也不在频道里，那我在哪？")
    state = group_state.get_group_state(id)

    if state is GameState.DISCONNECTED:
            content =   '对喔！通往外部和其他计算机的网线都还没有插上呢，可是网线被搞丢了QAQ\n' \
                        '根据以下线索寻找网线：\n' \
                        '线索1：熊曰：呋物眠我盜哮嗡哞有爾類盜哮爾噔森唬咬呱嚁物沒嗷覺破嗄咬果唬註破食嗚囑雜嗚盜噔住森洞嗅嘿嘶誒樣嚄寶更果麼爾拙嚄噔很類嘍 \n' \
                        '线索2：data:image/bmp;base64,Qk2QAAAAAAAAAD4AAAAoAAAAIgAAAAoAAAABAAEAAAAAAFIAAAASCwAAEgsAAAAAAAAAAAAA////AAAAAAAAAAAAAAAAAAAAAAcAAAAAAAAAAIAAAABXkD0DgAAAAFRQRQSAAAAAVlk9lIAAAABVlglkgAAAAEQAeAAAAAAAVAAAAAAAAAAAAAAAAAAAAAAA \n' \
                        '线索3：&#92;&#117;&#54;&#57;&#55;&#99;&#92;&#117;&#54;&#56;&#97;&#102;&#92;&#117;&#57;&#53;&#102;&#52;&#10; \n' \
                        '如果你找到了网线所在位置，请回复 /plug 地点+具体位置+编号'
            return content
    else:
        content = "网线已经插好啦！"
        return content

@on_message.regex(r"^\s*/插网线\s*(.+)$")
@on_message.regex(r"^\s*/plug\s*(.+)$")
async def plug():
    group_state = group_game_state_manager
    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        log.error("我不在群里，也不在频道里，那我在哪？")
    state = group_state.get_group_state(id)

    match = ctx.matched.regex
    info = match.group(1)
    # log.info("让我康康")
    # log.info(info)
    if state is not GameState.DISCONNECTED:
        content = "网线已经插好啦！"
        return content
    if info in ["图书馆+楼梯间+7","图书馆+楼梯间+七","library+楼梯间+7","library+楼梯间+七"]:
        group_state.update_state(id, GameState.LAN)
        content= "原来网线在图书馆七层楼梯间的仓库里！虽然互联网依然没有连接，但是局域网已经可以正常使用了，或许可以通过连接到其他电脑来找到联网方法！"
        return content
    else:
        return "好像不在这里呢"
