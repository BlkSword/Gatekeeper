# 安全日志覆盖策略检测

import subprocess
import re

def run_check():
    try:
        security_log_xml = subprocess.getoutput('wevtutil gl Security /f:xml')
        retention_match = re.search(r'<Retention>(\d)</Retention>', security_log_xml)
        status = retention_match.group(1) == "1" if retention_match else False
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "安全日志覆盖策略检测",
                    "status": status
                }]
            }
        }
    except:
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "安全日志覆盖策略检测",
                    "status": False
                }]
            }
        }

if __name__ == "__main__":
    print(run_check())