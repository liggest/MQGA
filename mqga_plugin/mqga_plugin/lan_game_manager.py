from collections import defaultdict
import random
from enum import Enum, auto

from mqga import log
from mqga_plugin.game_state_manager import group_game_state_manager, GameState

class IPFeature(Enum):
    """ IP功能 """
    ROLL = auto() # 掷骰子
    CLUE = auto() # 线索
    CRUSH = auto() # 全家桶卡死
    VIRUS = auto() # 中病毒

    def __str__(self) -> str:
        return self.name

class LANGameManager:
    def __init__(self):
        # 存储各个群的密码
        self.group_passwords = {}  # key: group_id, value: password
        self.user_group_ips = defaultdict(list) # key: (group_id, user_id), value: list of IP addresses
        self.ip_features = {}  # key: IP addresses, value: IP feature
        self.clue_assigned = defaultdict(int)  # key: group_id, value: 已分配线索的用户数量


    def scan_ip(self, group_id, user_id):
        """ 生成并返回IP地址 """
        user_group_key = (group_id, user_id)
        if self.user_group_ips[user_group_key]:
            return self.user_group_ips[user_group_key]
        
        # 生成新的IP地址
        new_ips = [f"192.168.1.{random.randint(2, 254)}" for _ in range(3)]
        self.user_group_ips[user_group_key].extend(new_ips)

        # 分配功能
        if self.clue_assigned[group_id] < 3:
            # 分配一个CLUE和其他随机功能
            clue_ip = random.choice(new_ips)
            self.ip_features[clue_ip] = IPFeature.CLUE
            for ip in new_ips:
                if ip != clue_ip:
                    self.ip_features[ip] = random.choice([f for f in IPFeature if f != IPFeature.CLUE])
            self.clue_assigned[group_id] += 1
        else:
            # 否则，随机分配其他功能
            for ip in new_ips:
                self.ip_features[ip] = random.choice(list(IPFeature))
        return new_ips

    def ping_ip(self, group_id, user_id, ip_address):
        """ 根据IP地址返回结果 """
        if ip_address in self.user_group_ips[group_id, user_id]: #其实应该把所有相同群的 ip 合起来的数据，这个函数不应该需要 user_id
            feature = self.ip_features[ip_address]
            if feature == IPFeature.CLUE:
                return "该 IP 地址是线索"
            elif feature == IPFeature.CRUSH:
                return "该 IP 地址是崩溃"
            elif feature == IPFeature.ROLL:
                return "该 IP 地址是掷骰子"
            elif feature == IPFeature.VIRUS:
                return "该 IP 地址是病毒"
        else:
            return "该 IP 地址不存在"

    def login(self, group_id, password):
        """ 验证密码并更新状态 """
        correct_password = self.group_passwords.get(group_id, "default_password")
        if password == correct_password:
            self.get_group_state(group_id).stage = GameState.INTERNET
            return True
        else:
            return False

LAN_game_manager = LANGameManager()