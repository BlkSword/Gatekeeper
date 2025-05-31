# 远程注册表访问检测

import subprocess
import re

def run_check():
    try:
        reg_output = subprocess.getoutput('reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v RemoteRegAccessPaths')
        paths_match = re.search(r'RemoteRegAccessPaths\s+REG_MULTI_SZ\s+(.+)', reg_output)
        actual_paths = paths_match.group(1).split('\\0') if paths_match else "未配置"
        
        status = actual_paths == "未配置" or len(actual_paths) <= 2
        
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "Remote Registry Paths Check",
                    "status": status
                }]
            }
        }
    except:
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "Remote Registry Paths Check",
                    "status": False
                }]
            }
        }

if __name__ == "__main__":
    print(run_check())