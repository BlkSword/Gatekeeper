# 账户登录事件检测

import subprocess
import re

def run_check():
    try:
        audit_policy = subprocess.getoutput('auditpol /get /category:*')
        status = bool(re.search(r"Logon\s+Success\s+Failure", audit_policy))
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "账户登录事件检测",
                    "status": status
                }]
            }
        }
    except:
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "账户登录事件检测",
                    "status": False
                }]
            }
        }

if __name__ == "__main__":
    print(run_check())