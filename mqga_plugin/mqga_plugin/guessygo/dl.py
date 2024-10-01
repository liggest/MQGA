
import httpx
import zipfile
import json
import random
from datetime import datetime

from mqga.log import log


from typing import TYPE_CHECKING

from mqga import on_event,on_message, EventType
from mqga_plugin.toolz import SimpleConfig

import mqga_plugin.guessygo as guessygo

if TYPE_CHECKING:
    from mqga.plugin.module import PluginModule
    guessygo: PluginModule

headers = {
    "Referer": "https://ygocdb.com",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36"
}

class Card_Poor:
    def __init__(self):
        self.Card_List = []
        self.Card_Data = {}

    def update(self, data:dict):
        self.Card_Data = data
        max = len(data)
        if max>0:
            self.Card_List = []
            for cid in data : 
                self.Card_List.append(cid)
    
    def len(self):
        return len(self.Card_List)
    
    def pick(self):
        cid = self.Card_List[random.randint(0,len(self.Card_List)-1)]
        return self.Card_Data[cid]
    
    def get(self, cid):
        return self.Card_Data[cid]

card_poor = Card_Poor()

class guessygoZip(SimpleConfig(guessygo.data_dir / "version.toml")):
    lastTime: str = ""
    version_url: str = "https://ygocdb.com/api/v0/cards.zip.md5?callback=gu"
    md5: str = ""

@on_event.of(EventType.WSReady)
@on_message.full_match(r"更新卡包")    
async def update():
    zip_file = guessygo.data_dir / "cards.zip"
    try:
        config = guessygoZip.get()
        if config.lastTime == datetime.now().strftime("%Y-%m-%d"):  # 每日更新
            return
        async with httpx.AsyncClient(headers=headers, timeout=(10,15)) as client:
            r = await client.get(config.version_url)
            # r = httpx.get(config.version_url,headers=headers, timeout=(10,15))
            if r.status_code != 200:
                log.error(f"[{r.status_code}]无法连接网站{r.url}")
                return
            if r.text == config.md5:
                log.info("[guessygo]卡包未更新")
                return
            config.md5 = r.text
            config.lastTime = datetime.now().strftime("%Y-%m-%d")
            config.save()
            url = "https://ygocdb.com/api/v0/cards.zip"
            r = await client.get(url)
            # r = httpx.get(url,headers=headers, timeout=(10,15))
            if r.status_code != 200:
                log.error(f"[{r.status_code}]无法连接网站{r.url}")
                return
        try:
            with open(zip_file,"wb") as f:
                f.write(r.content)
        except Exception as e:
            log.error(e)
            return
        log.info("[guessygo]卡包已更新")
    finally:
        cards_Info = None
        with zipfile.ZipFile(zip_file,"r") as zip_ref:
            with zip_ref.open("cards.json") as f:
                cards_Info = json.load(f)
                global card_poor
                card_poor.update(cards_Info)
        log.info(f"[guessygo]卡池已加载{len(cards_Info)}张卡牌")

def Get_Poor():
    global card_poor
    return card_poor
