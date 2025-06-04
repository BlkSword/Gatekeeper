# 账户登录事件检测

import subprocess
import re
import json

def run_check():
    try:
        audit_policy = subprocess.getoutput('auditpol /get /category:*')
        status = bool(re.search(r"Logon\s+Success\s+Failure", audit_policy))
        return {
            "check_name": "账户锁定阈值",
            "status": status
        }
    except:
        return {
            "check_name": "账户锁定阈值",
            "status": False
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False)) 