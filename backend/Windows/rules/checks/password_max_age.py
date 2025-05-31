# 密码最长使用期检测
import subprocess
import re

def run_check():
    try:
        policy = subprocess.getoutput('net accounts')
        match = re.search(r"Maximum password age\s+(\d+)", policy)
        value = int(match.group(1)) if match else 0
        return {
            "check_name": "密码最长使用期(天)",
            "status": value <= 90 if value else False
        }
    except Exception as e:
        return {
            "check_name": "密码最长使用期(天)",
            "status": False,
            "error": str(e)
        }
    
if __name__ == "__main__":
    print(run_check())