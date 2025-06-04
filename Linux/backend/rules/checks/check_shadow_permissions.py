# /etc/shadow 文件权限检测

import subprocess
import json

def run_check():
    try:
        # 获取文件权限
        shadow_perm = subprocess.getoutput("stat -c %a /etc/shadow 2>/dev/null").strip()
        # 判断权限是否为 600
        status = shadow_perm == "600"
        return {
            "check_name": "/etc/shadow 文件权限",
            "status": status,
            "details": {"permission": shadow_perm or "未配置"}
        }
    except Exception as e:
        return {
            "check_name": "/etc/shadow 文件权限",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))