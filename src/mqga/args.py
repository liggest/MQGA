
import sys
import argparse

parser = argparse.ArgumentParser(description="MQGA Process argparse:")
# 调试参数
parser.add_argument('-D', '--debug', action='store_true', help='开启debug模式')
parser.add_argument('-L', '--legacy', action='store_true', help='LEGACY')
parser.add_argument('-R', '--reload', action='store_true', help='开发模式下的热重载')
# config参数
parser.add_argument('-a', '--appid', type=str, help='机器人ID, 在 https://q.qq.com/bot/#/developer/developer-setting 获取')
parser.add_argument('-t', '--token', type=str, help='机器人令牌, 在 https://q.qq.com/bot/#/developer/developer-setting 获取')
parser.add_argument('-s', '--secret', type=str, help='机器人密钥, 在 https://q.qq.com/bot/#/developer/developer-setting 获取')
parser.add_argument('-p', '--public', action='store_true', help='指明该机器人是公域')
parser.add_argument('-b', '--sandbox', action='store_true', help='运行在沙盒频道中')
parser.add_argument('-c', '--config', type=str, help='从指定的config.yml的路径加载config信息')
parser.add_argument('-d', '--dump', type=str, help='导出config信息到指定的config文件夹')

args = parser.parse_args()

# for i in range(len(sys.argv)):
#     if sys.argv[i] == '-R' or sys.argv[i] == '--reload':
#         del sys.argv[i]
#         break
if '-R' in sys.argv:
    sys.argv.remove('-R')
if '--reload' in sys.argv:
    sys.argv.remove('--reload')
    
