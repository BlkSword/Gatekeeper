# SSH Banner检测

import subprocess
import re
import os
import json

def run_check():
    try:
        ssh_config = subprocess.getoutput("cat /etc/ssh/sshd_config 2>/dev/null")
        banner_match = re.search(r"^Banner\s+(/[\w/.]+)", ssh_config, re.MULTILINE)
        
        if banner_match:
            banner_path = banner_match.group(1)
            file_exists = os.path.exists(banner_path)
        else:
            file_exists = False

        return {
            "check_name": "SSH Banner配置检测",
            "status": bool(banner_match and file_exists)
        }
    except Exception as e:
        return {
            "check_name": "SSH Banner配置检测",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))