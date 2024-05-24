
import re

from ygoutil.source import BaiGe
from ygoutil.source.baige.misc import Site

from mqga import on_message, context as ctx
from mqga_plugin.toolz.filter import Filters
from mqga_plugin.toolz.markdown import register_markdown, Snippet
from mqga_plugin.toolz.markdown.keyboard import InteractButton, CommandButton
from mqga_plugin.toolz.markdown.keyboard import by_buttons, ButtonInteractEventPayload, InteractionResult

from mqga_plugin.test.inspect import image

# DefaultCard = 60764583  # 羊
BaseUrl = "https://cdn.233.momobako.com/ygopro/"
Cover = f"{BaseUrl}textures/cover.jpg"
OnePage = 8
Params = {f"card{i}": Cover for i in range(OnePage)}
Params["at"] = Snippet.at("{user_id}")
Params["query"] = "「{query}」的查询结果"

card_table_md = register_markdown("卡表模板", "陈列 8 张卡片", Params)

page_ptn = re.compile(r"(页=\d+)\s*$")

left_btn = InteractButton("上一页", "yc_l", "")
page_btn = CommandButton("0 / 0", "")
right_btn = InteractButton("下一页", "yc_r", "")

@right_btn.on_interact
@left_btn.on_interact
async def new_page():
    payload: ButtonInteractEventPayload = ctx.payload
    query = payload.data.button.data
    if query:
        await (await ygocard(query))
    return InteractionResult.操作成功

def get_page(query: str):
    page = 1
    if m := page_ptn.search(query):
        query = query[:m.start()].rstrip()
        page = int(m.group(1).removeprefix("页="))
    page -= 1
    return page, query

async def baige_ids(query: str):
    baige = BaiGe()
    return await baige.list_ids_from_query(query)

def page_range(current: int, items, per_page: int):
    total, remain = divmod(len(items), per_page)
    if remain:
        total += 1
    last = total - 1
    if current > last:
        current = last
    return current, last

def update_page_btn(current: int, last: int, query: str, 
                    left_btn: InteractButton, right_btn: InteractButton, mid_btn: CommandButton):
    if current == 0:
        left_btn.text = "首页"
        left_btn.data = ""
    else:
        left_btn.text = "上一页"
        left_btn.data = f"{query} 页={current}"
    if current == last:
        right_btn.text = "尾页"
        right_btn.data = ""
    else:
        right_btn.text = "下一页"
        right_btn.data = f"{query} 页={current + 2}"
    mid_btn.text = f"{current + 1} / {last + 1}"
    mid_btn.command = f"查卡 {query} 页="
    return left_btn, mid_btn, right_btn

def ctx_user_id():
    if isinstance(ctx.payload, ButtonInteractEventPayload):
        return ctx.payload.data.user_id
    return ctx.message.author.id

@on_message.filter_by(Filters.command("yc", ignore_case=True, context=ctx))
@on_message.filter_by(Filters.command("查卡", context=ctx))
@on_message.filter_by(Filters.command("卡查", context=ctx))
async def ygocard(query=""):
    query = query or str("".join(ctx.matched.filter_by)).strip()
    page, query = get_page(query)
    params = Params.copy()
    ids = await baige_ids(query)
    if not ids:
        return "再怎么找也没有啦"
    page, last = page_range(page, ids, OnePage)
    page_cards = ids[page * OnePage: (page + 1) * OnePage]
    if len(page_cards) == 1:
        return image(Site.card_pic_url(page_cards[0].id))
    for idx, card in enumerate(page_cards):
    # async for card in Pager(baige.gen_ids_from_query(query), slicer=slice(page, page + 1, OnePage)):
        params[f"card{idx}"] = Site.card_pic_url(card.id)
    params["at"] = params["at"].format(user_id=ctx_user_id())
    params["query"] = params["query"].format(query=query)
    row = update_page_btn(page, last, query, left_btn, right_btn, page_btn)
    # return ctx.bot.api.reply_md(ctx.payload, by_template(card_table_md.with_params(params)), by_buttons([left_btn, right_btn]))
    return ctx.bot.api.reply_md(ctx.payload, card_table_md.with_params(params), by_buttons(row))
