# Root远程登录检测

import subprocess
import re
import json

def run_check():
    try:
        # 检测SSH配置
        ssh_config = subprocess.getoutput("cat /etc/ssh/sshd_config 2>/dev/null")
        permit_root_ssh = re.search(r"^PermitRootLogin\s+(\w+)", ssh_config, re.MULTILINE)
        
        # 检测Telnet服务
        telnet_installed = "telnet" in subprocess.getoutput("dpkg -l | grep telnet")
        
        # 判断是否符合基线标准
        ssh_status = permit_root_ssh and permit_root_ssh.group(1).lower() == "no"
        telnet_status = not telnet_installed
        status = ssh_status and telnet_status
        
        return {
            "check_name": "Root远程登录",
            "status": bool(status),
            "details": {
                "SSH配置": permit_root_ssh.group(1) if permit_root_ssh else "未配置",
                "Telnet服务": "已安装" if telnet_installed else "未安装"
            }
        }
    except Exception as e:
        return {
            "check_name": "Root远程登录",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))