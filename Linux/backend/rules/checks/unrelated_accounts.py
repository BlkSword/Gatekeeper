# 无关账号检测

import subprocess
import json

def run_check():
    try:
        # 获取系统用户列表
        users = subprocess.getoutput("getent passwd | awk -F: '{print $1}'").split()
        target_accounts = ["adm", "lp", "ftp"]
        existing_accounts = [acc for acc in target_accounts if acc in users]
        
        # 判断是否符合基线标准
        status = not existing_accounts
        
        return {
            "check_name": "无关账号",
            "status": bool(status),
            "details": {
                "实际值": existing_accounts
            }
        }
    except Exception as e:
        return {
            "check_name": "无关账号",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))