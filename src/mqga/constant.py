from enum import IntEnum

class MsgType(IntEnum):
    Text = 0
    """ 文本 """
    TextImage = 1
    """ 图文混排 """
    Markdown = 2
    Ark = 3
    Embed = 4
    AT = 5

class FileType(IntEnum):
    图片 = 1 
    视频 = 2
    语音 = 3 
    文件 = 4

