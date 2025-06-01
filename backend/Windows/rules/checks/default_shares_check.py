# 默认共享检测脚本

import subprocess
import re
import json

def run_check():
    try:
        share_output = subprocess.getoutput('net share')
        default_shares = re.findall(r'(\w+\$)\s+', share_output)
        return {
            "check_name": "默认共享检测（C$、ADMIN$等）",
            "status": not bool(default_shares)
        }
    except Exception as e:
        return {"check_name": "默认共享检测（C$、ADMIN$等）", "status": False, "error": str(e)}
    
if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False)) 