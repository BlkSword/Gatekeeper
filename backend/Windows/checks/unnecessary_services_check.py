# 不必要服务禁用检测

import subprocess
import re

def run_check():
    check_name = "不必要的服务禁用检查"
    target_services = ["TELNET", "RemoteRegistry", "SMTP"]
    all_disabled = True
    
    try:
        for service in target_services:
            # 使用PowerShell获取服务启动类型
            ps_cmd = f"Get-Service -Name {service} -ErrorAction SilentlyContinue | Select-Object StartType"
            output = subprocess.getoutput(f'powershell "{ps_cmd}"')
            
            # 解析启动类型
            start_type_match = re.search(r"StartType\s+(\w+)", output)
            if not start_type_match:
                all_disabled = False
                continue
            start_type = start_type_match.group(1)
            if start_type != "Disabled":
                all_disabled = False
        
        return {
            "check_name": check_name,
            "status": all_disabled
        }
    except Exception as e:
        return {
            "check_name": check_name,
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    print(run_check())