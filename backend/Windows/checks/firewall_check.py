# 防火墙检测脚本

import subprocess
import re

def run_check():
    try:
        firewall_output = subprocess.getoutput('netsh advfirewall show allprofiles state')
        statuses = re.findall(r"状态\s+([^\n]+)", firewall_output)
        enabled_count = sum(1 for status in statuses if "启用" in status)
        
        return {
            "check_name": "Firewall Check",
            "status": enabled_count == 3
        }
    except Exception:
        return {"check_name": "Firewall Check", "status": False}
    
if __name__ == "__main__":
    print(run_check())