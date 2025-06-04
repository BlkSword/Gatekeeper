# SSH加密协议检测

import subprocess
import re
import json

def run_check():
    try:
        ssh_config = subprocess.getoutput("cat /etc/ssh/sshd_config 2>/dev/null")
        # 检测协议版本（应设置为 Protocol 2）
        protocol = re.search(r"^Protocol\s+(\d+)", ssh_config, re.MULTILINE)
        # 检测是否禁用弱加密算法（示例检测 Ciphers）
        ciphers = re.search(r"^Ciphers\s+(.+)", ssh_config, re.MULTILINE)
        
        # 直接判断状态：协议2且包含强加密算法
        status = (protocol and protocol.group(1) == "2" and 
                 ciphers and "aes256-ctr" in ciphers.group(1))
        
        return {
            "check_name": "SSH加密协议配置检测",
            "status": bool(status)
        }
    except Exception as e:
        return {
            "check_name": "SSH加密协议配置检测",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))