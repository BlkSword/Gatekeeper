# 文件所有权权限检测
import subprocess
import json

def run_check():
    try:
        priv_output = subprocess.getoutput('whoami /priv')
        has_privilege = "SeTakeOwnershipPrivilege" in priv_output and "Enabled" in priv_output
        
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "File Ownership Privilege Check",
                    "status": not has_privilege
                }]
            }
        }
    except:
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "File Ownership Privilege Check",
                    "status": False
                }]
            }
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False)) 