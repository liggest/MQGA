
import re
import httpx
import random 
# import base64
from math import sqrt
from io import BytesIO
from PIL import Image

from mqga import on_message, context as ctx
from mqga.q.message import ChannelMessage, GroupMessage
from mqga.log import log


from typing import TYPE_CHECKING
import mqga_plugin.guessygo as guessygo
if TYPE_CHECKING:
    from mqga.plugin.module import PluginModule
    guessygo: PluginModule


from mqga_plugin.guessygo.dl import Get_Poor,card_poor,headers
from mqga_plugin.guessygo.gameroom import GameState,game_rooms

types = ["马赛克","随机切割","旋转","描边","乱序"]

import asyncio
async def _do_timer(gid):
    room_info = game_rooms.get_room_state(gid)
    reply = ctx.bot.api.of(room_info.payload).reply_text
    await asyncio.sleep(90)
    await reply(room_info.payload, content="还有15s作答时间")
    await asyncio.sleep(30)
    reply = ctx.bot.api.of(room_info.payload).reply_media
    await reply(room_info.payload, 
                content=f"时间超时,游戏结束\n卡名是:\n{room_info.card['cn_name']}",
                file_or_url=f"https://cdn.233.momobako.com/ygopro/pics/{room_info.card['id']}.jpg",
            )
    game_rooms.del_room(gid)

@on_message.regex(r"\s*/猜卡游戏$")
async def start_game():
    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        id = -message.author.id
    room = game_rooms.get_room_state(id)
    if room is not None:
        return "已经有游戏在进行了"
    poor = card_poor
    if poor is None:
        log.debug("卡池为空,正在更新卡池")
        poor =  Get_Poor()
    max_index = 0
    card_data:dict = poor.pick()
    if card_data is None or poor.len() == 0:
        return "卡池没卡,请先更新卡池"
    while not await download_card_pictrue(card_data.get("id",0)) and max_index < 5:
        max_index = max_index+1
        card_data = poor.pick()
    if max_index >= 5:
        return "神奇,抽的全是白卡!"
    pictrue = draw_picture(card_data)
    new_room = GameState()
    new_room.auther = message.author.id
    new_room.payload = ctx.payload
    new_room.card = card_data
    new_room.picture = pictrue
    # task_end = asyncio.create_task(_do_timer(id))
    task_end = ctx.bot._em.background_task(_do_timer(id))
    new_room.task = task_end
    game_rooms.update_room_state(id,new_room)
    return ctx.bot.api.reply_media(ctx.payload, 
                                   file_or_url = pictrue, 
                                   content="请回答该图的卡名\n以“我猜xxx”格式回答\n(xxx需包含卡名1/4以上)\n或发“提示”得提示;“取消”结束游戏",
                                   )


@on_message.regex(r"^\s*我猜(.*)")
async def answer():
    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        id = -message.author.id
    room = game_rooms.get_room_state(id)
    if room is None:
        return
    match = ctx.matched.regex
    anser = match.group(1)
    need_length = len(room.card["cn_name"])//4
    if len(anser) < need_length:
        return "请输入", need_length, "字以上"
    anser_list = list(room.get_anser())
    log.debug(anser_list)
    anser, percentage = match_name(anser_list, anser)
    content = f"恭喜你答对了\n卡名是:\n{room.card['cn_name']}\n正确率:{percentage}%"
    if anser != room.card["cn_name"]:
        content = f"恭喜你答对了\n卡名是:\n{room.card['cn_name']}\n{anser}\n正确率:{percentage}%"
    if  percentage > 0:
        room.task.cancel()
        game_rooms.del_room(id)
        return ctx.bot.api.reply_media(ctx.payload, 
                    content=content,
                    file_or_url=f"https://cdn.233.momobako.com/ygopro/pics/{room.card['id']}.jpg",
                    )
    room.wrong_times = room.wrong_times + 1
    if room.wrong_times >= 6:
        room.task.cancel()
        game_rooms.del_room(id)
        return ctx.bot.api.reply_media(ctx.payload, 
                    content=f"很遗憾没有回答上来\n卡名是:\n{room.card['cn_name']}",
                    file_or_url=f"https://cdn.233.momobako.com/ygopro/pics/{room.card['id']}.jpg",
                    )
    game_rooms.update_room_state(id,room)
    return f"答案不对哦，加油啊。\n还有{6-room.wrong_times}次答题机会"

@on_message.regex(r"^\s*提示")
async def answer_hint():
    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        id = -message.author.id
    room = game_rooms.get_room_state(id)
    if room is None:
        return
    room.tick_times = room.tick_times + 1
    if room.tick_times > 3:
        return "  已经没有提示了,加油啊"
    game_rooms.update_room_state(id,room)
    return getCue(room.card,room.tick_times-1)

@on_message.regex(r"^\s*取消")
async def answer_cancel():
    message = ctx.message
    if isinstance(message, ChannelMessage):
        id = message.channel_id
    elif isinstance(message, GroupMessage):
        id = message.group_id
    else:
        id = -message.author.id
    room = game_rooms.get_room_state(id)
    if room is None:
        return
    if room.auther != message.author.id:
        return "只有猜题人可以取消"
    room.task.cancel()
    game_rooms.del_room(id)
    return ctx.bot.api.reply_media(ctx.payload, 
                content=f"游戏已取消\n卡名是:\n{room.card['cn_name']}",
                file_or_url=f"https://cdn.233.momobako.com/ygopro/pics/{room.card['id']}.jpg",
                )

async def download_card_pictrue(cid):
    pictrue_path = guessygo.data_dir / "pictures/"
    if not pictrue_path.exists():
        pictrue_path.mkdir(parents=True, exist_ok=True)
    pictrue_path = guessygo.data_dir / f"pictures/{cid}.jpg"
    if pictrue_path.exists():
        return True
    picherf = f"https://cdn.233.momobako.com/ygopro/pics/{cid}.jpg"
    async with httpx.AsyncClient() as client:
        # r = httpx.get(picherf,headers=headers, timeout=(10,15))
        r = await client.get(picherf,headers=headers, timeout=(10,15))
    if r.status_code != 200:
        log.error(f"[{r.status_code}]无法连接网站{r.url}")
        return False
    try:
        with open(pictrue_path,"wb") as f:
            f.write(r.content)
            return True
    except Exception as e:
        log.error(e)
        return False

def draw_picture(card_data: dict):
    cid = card_data.get("id",0)
    pictrue_path = guessygo.data_dir / f"pictures/{cid}.jpg"
    new_img:Image.Image = None
    with Image.open(pictrue_path) as pic:
        image_size  = (51, 108, 351, 408)
        if '灵摆' in card_data.get("text",{}).get("types",''):
            log.info(f"[{cid}]{card_data.get('cn_name','')}是灵摆怪兽")
            image_size  = (29, 105, 370, 358)
        new_img = pic.crop(image_size)
    match types[random.randint(0, len(types)-1)]:
        case "马赛克":
            return mosaic(new_img)
        case "随机切割":
            return cut(new_img)
        case "旋转":
            return rotate(new_img)
        case "描边":
            return blur(new_img)
        case "乱序":
            return randpic(new_img)
        

def mosaic(img: Image.Image):
    """500 / 10 = 50  500/30 = 16"""
    mosaic_size = 15 + 3 * random.randint(0, 5)
    width, height = img.size

    new_img = Image.new("RGBA", img.size)

    for mosaic_y in range(0, height-mosaic_size, mosaic_size):
        for mosaic_x in range(0, width-mosaic_size, mosaic_size):
            bloak_center_x = mosaic_x+int(mosaic_size/2)
            bloak_center_y = mosaic_y+int(mosaic_size/2)
            rgb = img.getpixel((bloak_center_x,bloak_center_y))
            for y in range(mosaic_size):
                for x in range(mosaic_size):
                    new_img.putpixel((mosaic_x+x, mosaic_y+y), rgb)
    return toBase64(new_img)


def cut(img: Image.Image):
    new_img = Image.new("RGBA", img.size)
    width, height = img.size
    w3,h3 = int(width/3), int(height/3)

    cut_path_x1, cut_path_y1, cut_path_x2, cut_path_y2 = random.randint(0, 2), random.randint(0, 2), random.randint(0, 2), random.randint(0, 2)

    for y in range(height):
        for x in range(width):
            if x > w3*cut_path_x1 and x < w3*(cut_path_x1+1) and y > h3*cut_path_y1 and y < h3*(cut_path_y1+1):
                rgb = img.getpixel((x, y))
                new_img.putpixel((x, y), rgb)
            elif x > w3*cut_path_x2 and x < w3*(cut_path_x2+1) and y > h3*cut_path_y2 and y < h3*(cut_path_y2+1):
                rgb = img.getpixel((x, y))
                new_img.putpixel((x, y), rgb)
            else:
                new_img.putpixel((x, y), (255, 255, 255, 255))
            if x in [0, w3, w3*2, width-1] or y in [0, h3, h3*2, height-1]:
                new_img.putpixel((x, y), (0, 0, 0, 255))
    return toBase64(new_img)

def rotate(img: Image.Image) :
    new_img = Image.new("RGBA", img.size)
    flip_img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    width, height = img.size
    flip = random.randint(0, 1)
    for y in range(height):
        for x in range(width):
            if y > x and x < width/2 and y < height/2:
                rgb = img.getpixel((x, y))
                new_img.putpixel((x, y), rgb)
            elif y < x and x > width/2 and y > height/2:
                rgb = img.getpixel((x, y))
                new_img.putpixel((x, y), rgb)
            elif y > height - x and x < width/2 and y > height/2:
                rgb = img.getpixel((x, y))
                new_img.putpixel((x, y), rgb)
            elif y < height - x and x > width/2 and y < height/2:
                rgb = img.getpixel((x, y))
                new_img.putpixel((x, y), rgb)
            else:
                rgb = flip_img.getpixel((x, y))
                if flip:
                    if len(rgb) == 4:
                        new_img.putpixel((x, y), (255-rgb[0], 255-rgb[1], 255-rgb[2], rgb[3]))
                    else:
                        new_img.putpixel((x, y), (255-rgb[0], 255-rgb[1], 255-rgb[2], 255))
                else:
                    new_img.putpixel((x, y),rgb)
    return toBase64(new_img)

def blur(img: Image.Image) :
    putColor = (0, 0, 0, 0)
    new_img = Image.new("RGBA", img.size, (255, 255, 255, 255))
    d = 25
    width, height = img.size
    if random.randint(0, 1) == 0:
        putColor = (255, 255, 255, 255)
        new_img = Image.new("RGBA", img.size, 'black')

    for y in range(height):
        for x in range(width):
            if (x < (width - 2)) and (y < (height - 2)):
                rgb = img.getpixel((x, y))
                rgb1 = img.getpixel((x+1, y))
                rgb2 = img.getpixel((x, y+1))
                if sqrt((rgb[0] - rgb1[0]) ** 2 + (rgb[1] - rgb1[1]) ** 2 + (rgb[2] - rgb1[2]) ** 2) >= d:
                    new_img.putpixel((x, y), putColor)
                elif sqrt((rgb[0] - rgb2[0]) ** 2 + (rgb[1] - rgb2[1]) ** 2 + (rgb[2] - rgb2[2]) ** 2) >= d:
                    new_img.putpixel((x, y), putColor)
            else:
                new_img.putpixel((x, y), (0, 0, 0))
    return toBase64(new_img)

def randpic(img: Image.Image):
    new_img = Image.new("RGBA", img.size)
    width, height = img.size
    w3,h3 = int(width/3), int(height/3)

    mappic = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)]

    for y in range(0,height-h3,h3):
        for x in range(0,width-w3,w3):
            index = random.randint(0,len(mappic)-1)
            mapface = mappic.pop(index)
            for dy in range(h3):
                for dx in range(w3):
                    rgb = img.getpixel((mapface[0]*w3+dx, mapface[1]*h3+dy))
                    new_img.putpixel((x+dx, y+dy), rgb)
    return toBase64(new_img)

def toBase64(img: Image.Image):
    output = BytesIO()
    img.save(output, format='png')
    contents = output.getvalue()
    return contents

def match_name(cardName:list, text:str):
    an = remove_punctuation(text).lower()
    if an == "":
        return "",0
    for anser in cardName:
        log.debug(anser)
        cn = remove_punctuation(anser).lower()
        if an in cn:
            return anser, len(an)*100//len(anser)
    return "",0

def remove_punctuation(text: str):
    punctuations = "\\\' ·~!@#$%^&*()-_+=\{\}[]|\;:\"<>,./?`"
    for p in punctuations:
        text = text.replace(p, "")
    return text


def getCue(card:dict, index:int):
    match index:
        case 0:
            return f"CN卡名一共{len(card.get('cn_name', ''))}字符"
        case 1:
            cue = card.get('text', {}).get('types', '')
            types = re.findall(r'\[(((?!\]).)*)\]', cue)
            if types:
                types_0 = types[0]
                if types_0:
                    cue = f"这张类型是{types_0[0]}"
            return cue
        case 2:
            text= remove_punctuation(card.get('cn_name', ''))
            if len(text) > 4:
                names = []
                max = len(text)/4
                for _ in range(int(max)):
                    world = text[random.randint(0,len(text)-1)]
                    text = text.replace(world,'')
                    names.append(world)
                return f"卡名包含{names}"
            else:
                describe = str(card.get('text', {}).get('pdesc', '')+card.get('text', {}).get('desc', '')).replace('\n','').replace('\r','')
                for _ in range(3):
                    names = re.findall(r'「([^」]*)」', describe)
                    if len(names) > 0:
                        for name in names: 
                            describe = describe.replace(name,'xxx')
                infos = list(filter(None,re.split(r'[。|，]',describe)))
                if len(infos)>2:
                    return f"{infos[random.randint(0,len(infos)-1)]}"
                else:
                    return describe
