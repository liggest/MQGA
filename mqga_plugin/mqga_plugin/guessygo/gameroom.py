from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from asyncio import Task

class GameState():
    """ 游戏状态 """
    auther = None # 猜题人
    payload = None # 追击聊天记录
    card: dict = None # 卡片信息
    picture = None # 图片信息
    last_time = 0 # 答题时间
    wrong_times = 0 # 错误次数
    tick_times = 0 # 提示次数
    answer_times = None # 答题次数
    task: Task = None # 任务

    def get_anser(self)-> list:
        namelist = ["cn_name","nwbbs_n","cnocg_n","md_name","jp_name","jp_ruby","en_name","sc_name"]
        return list({self.card.get(name,'') for name in namelist})

class GameRoom:
    """ 群游戏状态管理器 """
    def __init__(self):
        self.group_states = {}  # key: group_id, value: GroupGameState

    def get_room_state(self, group_id) -> GameState|None:
        """ 获取指定房间状态 """
        return self.group_states.get(group_id, None)

    def update_room_state(self, group_id, new_state):
        """ 更新群所处的房间阶段 """
        self.group_states[group_id] = new_state
    
    def del_room(self, group_id):
        """ 删除指定房间 """
        self.group_states.pop(group_id)

game_rooms = GameRoom()
