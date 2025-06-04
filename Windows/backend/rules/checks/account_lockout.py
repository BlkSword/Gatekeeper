# 账户锁定阈值

import subprocess
import os
import re
import json

def run_check():
    try:
        temp_path = os.path.join(os.environ['TEMP'], 'secpol.cfg')
        subprocess.getoutput(f'secedit /export /cfg {temp_path}')
        result = subprocess.getoutput(f'find "LockoutThreshold" {temp_path}')
        match = re.search(r"LockoutThreshold\s+=\s+(\d+)", result)
        value = int(match.group(1)) if match else 0
        return {
            "check_name": "账户锁定阈值",
            "status": bool(value <= 3) if value else False  # 确保布尔值
        }
    except Exception as e:
        return {
            "check_name": "账户锁定阈值",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False)) 