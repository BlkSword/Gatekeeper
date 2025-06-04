# SNMP团体字检测

import subprocess
import re
import json

def run_check():
    try:
        snmp_config = subprocess.getoutput("cat /etc/snmp/snmpd.conf 2>/dev/null")
        # 检测只读团体字（rocommunity）和读写团体字（rwcommunity）
        ro_community = re.findall(r"rocommunity\s+(\w+)", snmp_config)
        rw_community = re.findall(r"rwcommunity\s+(\w+)", snmp_config)
        
        # 直接判断状态：不包含默认值public/private
        status = (not any("public" in c for c in ro_community) and 
                 not any("private" in c for c in rw_community))
        
        return {
            "check_name": "SNMP团体字配置检测",
            "status": bool(status)
        }
    except Exception as e:
        return {
            "check_name": "SNMP团体字配置检测",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))