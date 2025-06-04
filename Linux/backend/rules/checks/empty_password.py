# 空口令账号检测

import subprocess
import json

def run_check():
    try:
        # 获取shadow文件内容
        shadow_content = subprocess.getoutput("sudo cat /etc/shadow 2>/dev/null")
        empty_users = [line.split(":")[0] for line in shadow_content.splitlines() if line.split(":")[1] in ["!", "*", ""]]
        
        # 判断是否符合基线标准
        status = not empty_users
        
        return {
            "check_name": "空口令账号",
            "status": bool(status),
            "details": {
                "实际值": empty_users
            }
        }
    except Exception as e:
        return {
            "check_name": "空口令账号",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))