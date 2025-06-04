# Telnet禁用检测

import subprocess
import re
import os
import json

def run_check():
    try:
        # 检测 Telnet 服务状态（是否运行）
        telnet_status = subprocess.getoutput("systemctl is-active telnet 2>/dev/null")
        # 检测 Telnet 是否安装（Debian/Ubuntu 用 dpkg，RHEL/CentOS 用 rpm）
        telnet_installed = "telnetd" in subprocess.getoutput("dpkg -l | grep telnet 2>/dev/null") or \
                          "telnet-server" in subprocess.getoutput("rpm -qa | grep telnet 2>/dev/null")
        
        # 直接判断状态：未安装且未运行时为True
        status = not telnet_installed and telnet_status != "active"
        
        return {
            "check_name": "Telnet服务禁用检测",
            "status": bool(status)
        }
    except Exception as e:
        return {
            "check_name": "Telnet服务禁用检测",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))