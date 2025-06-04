# 特权用户检测

import subprocess
import re
import json

def run_check():
    try:
        # 获取用户列表
        users_output = subprocess.getoutput("getent passwd | awk -F: '{print $1,$3}'")
        users = users_output.splitlines()
        # 检测特权用户（UID < 1000 且非 root）
        privileged_users = [
            user.split()[0] 
            for user in users 
            if int(user.split()[1]) < 1000 and user.split()[0] != "root"
        ]
        return {
            "check_name": "特权用户检测",
            "status": not bool(privileged_users),
            "details": {"privileged_users": privileged_users}
        }
    except Exception as e:
        return {
            "check_name": "特权用户检测",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))