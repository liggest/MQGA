
from ygoutil.card.ids import IDCard
from ygoutil.source import BaiGePage
from ygoutil.source.baige.misc import BaiGeURLUnit

from mqga import on_message, context as ctx

from mqga_plugin.toolz.markdown import Snippet
from mqga_plugin.toolz.markdown.keyboard import by_buttons, InteractButton, CommandButton, JumpButton
from mqga_plugin.toolz.markdown.keyboard import ButtonInteractEventPayload, InteractionResult
from mqga_plugin.toolz.filter import Filters

from mqga_plugin.md import md_test, content2params
from mqga_plugin.ygocard.baige import get_page, baige_ids, page_range, update_page_btn, ctx_user_id

OnePage = 10
OneBtnRow = 5

left_btn = InteractButton("上一页", "yc2_l", "")
page_btn = CommandButton("0 / 0", "")
right_btn = InteractButton("下一页", "yc2_r", "")

@right_btn.on_interact
@left_btn.on_interact
async def new_page():
    payload: ButtonInteractEventPayload = ctx.payload
    query = payload.data.button.data
    if query:
        await (await ygocard2(query))
    return InteractionResult.操作成功

card_btns = [InteractButton("x", f"yc2_card{i}", "") for i in range(OnePage)]

async def to_card_info():
    payload: ButtonInteractEventPayload = ctx.payload
    card_id = payload.data.button.data
    if card_id:
        await (await card_info(card_id))
    return InteractionResult.操作成功

for card_btn in card_btns:
    card_btn.on_interact(to_card_info)

def update_card_btns(ids: list[IDCard]):
    row = []
    for idx, (btn, card) in enumerate(zip(card_btns, ids)):
        btn.text = f"{idx} {card.name}"
        btn.data = str(card.id)
        row.append(btn)
        if len(row) == OneBtnRow:
            yield row
            row = []
    if row:
        yield row

# @on_message.filter_by(Filters.command("2yc", ignore_case=True, context=ctx))
@on_message.filter_by(Filters.command(cmd_name := "文字查卡", context=ctx))
@on_message.filter_by(Filters.command("文字卡查", context=ctx))
async def ygocard2(query=""):
    query = query or str("".join(ctx.matched.filter_by)).strip()
    page, query = get_page(query)
    ids = await baige_ids(query)
    if not ids:
        return "再怎么找也没有啦"
    page, last = page_range(page, ids, OnePage)

    page_cards = ids[page * OnePage: (page + 1) * OnePage]
    if len(page_cards) == 1:
        return await card_info(page_cards[0].id)
    card_content = "\n".join(f"{idx} {card.name}" for idx, card in enumerate(page_cards))
    md_content = f"""{Snippet.at(ctx_user_id())} 「{query}」的查询结果\n```\n{card_content}\n```"""
    row = update_page_btn(page, last, query, left_btn, right_btn, page_btn)
    page_btn.command = f"{cmd_name} {query} 页="
    return ctx.bot.api.reply_md(ctx.payload, 
                                md_test.with_params(content2params(md_content)), 
                                by_buttons(*update_card_btns(page_cards), row))

async def card_info(card_id: str):
    card = await BaiGePage().from_id(card_id)
    if card:
        md_content = f"""{Snippet.at(ctx_user_id())}\n```\n{card.info()}\n```"""
        urls: BaiGeURLUnit = card._url_unit
        btns = None
        if urls:
            row1 = [JumpButton(text, url) for text, url in (
                ("百鸽", urls.url),
                ("数据库", urls.database),
                ("Q&A", urls.QA),
                ("Wiki", urls.wiki),
            )]
            row2 = [JumpButton(text, url) for text, url in (
                ("Yugipedia", urls.yugipedia),
                ("OurOcg", urls.ourocg),
                ("脚本", urls.script),
                ("裁定", urls.ocg_rule),
            )]
            btns = by_buttons(row1, row2)
        return ctx.bot.api.reply_md(ctx.payload, md_test.with_params(content2params(md_content)), btns)
