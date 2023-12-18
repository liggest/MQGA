from collections import defaultdict
import random
import string
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

class CaesarCipherInfo:
    """ 凯撒密码信息 """
    def __init__(self):
        self.original_string = ""
        self.offset = 0
        self.replacement_pair = ("", "")
        self.final_answer = ""

    def generate_final_answer(self):
        """ 生成并存储最终的凯撒密码答案 """
        # 替换操作
        trans_table = str.maketrans(self.replacement_pair[0] + self.replacement_pair[1],
                                    self.replacement_pair[1] + self.replacement_pair[0])
        replaced_str = self.original_string.translate(trans_table)

        # 移位操作
        self.final_answer = ''.join(
            chr((ord('a') + (ord(char) - ord('a') + self.offset) % 26) if char.isalpha() else char)
            for char in replaced_str
        )
        return self.final_answer

class LANGameManager:
    def __init__(self):
        # 存储各个群的密码
        self.group_passwords = {}  # key: group_id, value: password
        self.user_group_ips = defaultdict(list) # key: (group_id, user_id), value: list of IP addresses
        self.ip_features = {}  # key: IP addresses, value: IP feature
        self.clue_assigned = defaultdict(int)  # key: group_id, value: 已分配线索的用户数量
        self.clue_call_count = defaultdict(int) # key: group_id, value: 线索函数的调用数量
        self.caesar_cipher_info = defaultdict(CaesarCipherInfo) # key: group_id, value: CaesarCipherInfo


    def scan_ip(self, group_id, user_id)->list:
        """ 生成并返回IP地址 """
        user_group_key = (group_id, user_id)
        if self.user_group_ips[user_group_key]:
            return self.user_group_ips[user_group_key]
        
        # 生成新的IP地址
        new_ips = [f"192.168.1.{random.randint(2, 254)}" for _ in range(3)]
        self.user_group_ips[user_group_key].extend(new_ips)

        # 分配功能
        if self.clue_assigned[group_id] < 3:
            # 前三个用户分配一个CLUE和其他随机功能
            clue_ip = random.choice(new_ips)
            self.ip_features[clue_ip] = IPFeature.CLUE
            for ip in new_ips:
                if ip != clue_ip:
                    self.ip_features[ip] = random.choice([f for f in IPFeature if f != IPFeature.CLUE])
            self.clue_assigned[group_id] += 1
        else:
            # 后面用户随机分配其他功能
            for ip in new_ips:
                self.ip_features[ip] = random.choice(list(IPFeature))
        return new_ips

    def ping_ip(self, group_id, user_id, ip_address)->str:
        """ 根据IP地址返回结果 """
        if ip_address in self.user_group_ips[group_id, user_id]:
            feature = self.ip_features[ip_address]
            if feature == IPFeature.CLUE:
                return self.clue(group_id)
            elif feature == IPFeature.CRUSH:
                return "该 IP 地址是崩溃" #TODO
            elif feature == IPFeature.ROLL:
                return self.roll()
            elif feature == IPFeature.VIRUS:
                return "该 IP 地址是病毒" #TODO
        else:
            return "该 IP 地址不存在"

    def can_login(self, group_id, password)->bool:
        """ 验证密码并更新状态 """
        correct_password = self.group_passwords.get(group_id) #TODO:如果用户上来输入一个空，是不是也可以？
        if password == correct_password:
            return True
        else:
            return False
    
    def roll(self):
        content = '你连接到了一台掷骰子的主机\n'
        content += f'你掷出了：{random.randint(1, 6)}'
        return content
    
    def clue(self, group_id) -> str:
        """ 根据调用次数返回不同类型的数据 """
        # TODO:计数还是不大对，一个人反复访问三次一个地址也可以，不过也不错
        cipher_info = self.caesar_cipher_info[group_id]
        call_count = self.clue_call_count[group_id]
        self.clue_call_count[group_id] += 1

        content = '你连接到了一台有线索的主机\n'

        if call_count % 3 == 0:
            # 第一次调用，返回字母字符串
            cipher_info.original_string = self.generate_random_string()
            return content+"线索1："+cipher_info.original_string
        elif call_count % 3 == 1:
            # 第二次调用，返回数字
            cipher_info.offset = self.generate_random_number()
            return content+"线索2："+str(cipher_info.offset)
        else:
            # 第三次调用，返回替换对
            cipher_info.replacement_pair = self.generate_replacement_pair()
            answer = cipher_info.generate_final_answer() 
            self.group_passwords[group_id] = answer
            log.info(f"解密结果：{answer}")
            
            return content+"线索3："+f'{cipher_info.replacement_pair}\n'+'三条线索已找齐'

    def generate_random_string(self, length_range=(5, 8)):
        """ 生成随机字母组成的字符串 """
        length = random.randint(*length_range)
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    def generate_random_number(self, number_range=(1, 10)):
        """ 生成随机数字 """
        # TODO:应该正负都有可能
        return random.randint(*number_range)

    def generate_replacement_pair(self):
        """ 生成随机替换对 """
        a, b = random.sample(string.ascii_lowercase, 2)
        return (a, b)

LAN_game_manager = LANGameManager()