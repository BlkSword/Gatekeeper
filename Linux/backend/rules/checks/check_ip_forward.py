# 获取数据包转发配置

import subprocess
import os
import re
import json

def run_check():
    try:
        
        ip_forward = subprocess.getoutput("sysctl net.ipv4.ip_forward 2>/dev/null")
        forward_value = re.search(r"net\.ipv4\.ip_forward\s*=\s*(\d+)", ip_forward)
        
        value = forward_value.group(1) if forward_value else "未配置"
        # 判断是否符合基线标准（值为0）
        status = (value == "0")
        return {
            "check_name": "关闭数据包转发（非路由系统）",
            "status": bool(status)
        }
    except Exception as e:
        return {
            "check_name": "关闭数据包转发（非路由系统）",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))