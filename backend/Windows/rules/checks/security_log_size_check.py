# 安全日志大小检测

import subprocess
import re
import json

def run_check():
    try:
        security_log_xml = subprocess.getoutput('wevtutil gl Security /f:xml')
        max_size_match = re.search(r'<MaxSize>(\d+)</MaxSize>', security_log_xml)
        if max_size_match:
            max_size_mb = int(max_size_match.group(1)) // (1024*1024)
            status = max_size_mb >= 2048
        else:
            status = False
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "安全日志大小检测",
                    "status": status
                }]
            }
        }
    except:
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "安全日志大小检测",
                    "status": False
                }]
            }
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False)) 