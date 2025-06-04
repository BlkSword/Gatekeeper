# 登录超时检测

import subprocess
import re
import os
import json

def run_check():
    try:
        ssh_config = subprocess.getoutput("cat /etc/ssh/sshd_config 2>/dev/null")
        interval_match = re.search(r"^ClientAliveInterval\s+(\d+)", ssh_config, re.MULTILINE)
        count_match = re.search(r"^ClientAliveCountMax\s+(\d+)", ssh_config, re.MULTILINE)
        
        interval = int(interval_match.group(1)) if interval_match else 0
        count = int(count_match.group(1)) if count_match else 0
        total_timeout = interval * count if interval > 0 and count > 0 else 0

        return {
            "check_name": "SSH登录超时检测",
            "status": bool(total_timeout <= 600) if (interval_match and count_match) else False
        }
    except Exception as e:
        return {
            "check_name": "SSH登录超时检测",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))