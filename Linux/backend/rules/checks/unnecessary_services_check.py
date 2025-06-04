# 不必要服务检测

import subprocess
import re
import os
import json

def run_check():
    try:
        # 检测服务安装状态
        def is_service_installed(service):
            return (f"{service}" in subprocess.getoutput(f"dpkg -l | grep {service} 2>/dev/null") or 
                   f"{service}" in subprocess.getoutput(f"rpm -qa | grep {service} 2>/dev/null"))
        
        # 检测服务运行状态
        def is_service_active(service):
            status = subprocess.getoutput(f"systemctl is-active {service} 2>/dev/null")
            return status == "active"

        # 目标服务列表
        target_services = ["telnet", "nfs", "rpcbind"]
        status = True  # 默认符合
        
        for service in target_services:
            if is_service_installed(service) and is_service_active(service):
                status = False  # 发现违规服务
                break
                
        return {
            "check_name": "不必要服务禁用检测",
            "status": status
        }
    except Exception as e:
        return {
            "check_name": "不必要服务禁用检测",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))