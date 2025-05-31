# 远程关机权限检测

import subprocess

def run_check():
    try:
        priv_output = subprocess.getoutput('whoami /priv')
        has_privilege = "SeRemoteShutdownPrivilege" in priv_output and "Enabled" in priv_output
        
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "Remote Shutdown Privilege Check",
                    "status": not has_privilege
                }]
            }
        }
    except:
        return {
            "security_policy": {
                "checks": [{
                    "check_name": "Remote Shutdown Privilege Check",
                    "status": False
                }]
            }
        }

if __name__ == "__main__":
    print(run_check())