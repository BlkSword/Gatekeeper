# 账户管理检测

import subprocess
import re
import json

def run_check():
    try:
        audit_policy = subprocess.getoutput('auditpol /get /category:*')
        status = bool(re.search(r"User Account Management\s+Success\s+Failure", audit_policy))
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "账户管理检测",
                    "status": status
                }]
            }
        }
    except:
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "账户管理检测",
                    "status": False
                }]
            }
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False)) 