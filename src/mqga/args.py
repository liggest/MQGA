
import argparse

parser = argparse.ArgumentParser(description="MQGA Process argparse:")
parser.add_argument('-a', '--appid', type=str, help='机器人ID, 在 https://q.qq.com/bot/#/developer/developer-setting 获取')
parser.add_argument('-t', '--token', type=str, help='机器人令牌, 在 https://q.qq.com/bot/#/developer/developer-setting 获取')
parser.add_argument('-s', '--secret', type=str, help='机器人密钥, 在 https://q.qq.com/bot/#/developer/developer-setting 获取')
parser.add_argument('-c', '--config', type=str, help='从指定的config.yml的路径加载config信息')
parser.add_argument('-d', '--dump', type=str, help='导出config信息到指定的config文件夹')
parser.add_argument('-D', '--debug', action='store_true', help='开启debug模式')

args = parser.parse_args()
