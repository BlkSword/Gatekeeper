# 获取 ICMP 重定向和源路由配置

import subprocess
import os
import re
import json

def run_check():
    try:
        
        sysctl_output = subprocess.getoutput("sysctl net.ipv4.conf.all.accept_redirects net.ipv4.conf.all.accept_source_route 2>/dev/null")
        accept_redirects = re.search(r"net\.ipv4\.conf\.all\.accept_redirects\s*=\s*(\d+)", sysctl_output)
        accept_source_route = re.search(r"net\.ipv4\.conf\.all\.accept_source_route\s*=\s*(\d+)", sysctl_output)
        
        redirect_value = accept_redirects.group(1) if accept_redirects else "未配置"
        source_route_value = accept_source_route.group(1) if accept_source_route else "未配置"
        
        # 判断是否符合基线标准（值为0）
        status = (redirect_value == "0" and source_route_value == "0")
        return {
            "check_name": "禁止 ICMP 重定向/源路由",
            "status": bool(status)
        }
    except Exception as e:
        return {
            "check_name": "禁止 ICMP 重定向/源路由",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))