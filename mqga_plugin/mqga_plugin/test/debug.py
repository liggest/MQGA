
from mqga import on_message
from mqga.log import log

@on_message.full_match(r"501咒文")
def res501():
    log.error("version:0.0.2\n/ping baidu.com -c 3\n/apikey xxx\n/apiping www.baidu.com -c 3")
    return "version:0.0.2\n/ping baidu.com -c 3\n/apikey xxx\n/apiping www.baidu.com -c 3"
    # 神秘内容，让官方接口返回 Http 501，而不是 json 格式的错误信息

@on_message.full_match(r"换个话题咒文")
def auto_reply():
    return "https" "://" "image.anosu.top/pixiv/direct?r18=1&keyword=azurlane"

@on_message.full_match(r"哑巴咒文")
def silence():
    return "675740d22de47d8ba3da92ee51770890"

