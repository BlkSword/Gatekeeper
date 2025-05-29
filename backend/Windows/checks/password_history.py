# 密码历史记录检测
import subprocess
import re

def run_check():
    try:
        policy = subprocess.getoutput('net accounts')
        match = re.search(r"Length of password history maintained\s+(\d+)", policy)
        value = int(match.group(1)) if match else 0
        return {
            "check_name": "密码历史记录",
            "status": value >= 24 if value else False
        }
    except Exception as e:
        return {
            "check_name": "密码历史记录",
            "status": False,
            "error": str(e)
        }
    
if  __name__ == "__main__":
    print(run_check())