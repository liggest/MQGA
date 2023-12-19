from enum import Enum

class GameState(Enum):
    """ 游戏状态 """
    DISCONNECTED = 0
    LAN = 1
    INTERNET = 2
    FULLSPEED = 3

    def __str__(self) -> str:
        return self.name

class GameStateManager:
    """ 群游戏状态管理器 """
    def __init__(self):
        self.group_states = {}  # key: group_id, value: GroupGameState
        self.login_states = {} # key: group_id, value: is_login

    def get_group_state(self, group_id):
        """ 获取群状态，如果不存在则创建新状态 """
        if group_id not in self.group_states:
            self.group_states[group_id] = GameState.DISCONNECTED
        return self.group_states[group_id]

    def update_state(self, group_id, new_state):
        """ 更新群所处的游戏阶段 """
        # new_state = GameState[new_state_str] if new_state_str in GameState.__members__ else None
        # log.info(GameState.__members__)
        # if new_state is None:
        #     raise ValueError(f"无效的游戏阶段: {new_state_str}")
        
        self.group_states[group_id] = new_state
    
    def get_login_state(self, group_id):
        if group_id not in self.login_states:
            self.login_states[group_id] = False
        return self.login_states[group_id]

    def login_success(self, group_id):
        self.login_states[group_id] = True
    
    def reset_state(self):
        """ 重置所有群状态 """
        self.group_states = {}

group_game_state_manager = GameStateManager()
