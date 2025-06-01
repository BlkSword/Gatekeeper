# 日志状态检测

import subprocess
import json

def run_check():
    try:
        system_log = subprocess.getoutput('wevtutil get-log System')
        security_log = subprocess.getoutput('wevtutil get-log Security')
        status = ("enabled: true" in system_log) and ("enabled: true" in security_log)
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "日志状态检测",
                    "status": status
                }]
            }
        }
    except:
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "日志状态检测",
                    "status": False
                }]
            }
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False)) 