# 密码最短使用期检测
import subprocess
import re
import json

def run_check():
    try:
        policy = subprocess.getoutput('net accounts')
        match = re.search(r"Minimum password age\s+(\d+)", policy)
        value = int(match.group(1)) if match else 0
        return {
            "check_name": "密码最短使用期(天)",
            "status": value >= 1 if value else False
        }
    except Exception as e:
        return {
            "check_name": "密码最短使用期(天)",
            "status": False,
            "error": str(e)
        }
    
if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False)) 