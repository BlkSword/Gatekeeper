# 密码生存期检测

import subprocess
import re
import json

def run_check():
    try:
        # 获取root密码生存期
        root_age = subprocess.getoutput("chage -l root 2>/dev/null")
        max_days_match = re.search(r"MaxDays\s*=\s*(\d+)", root_age)
        
        max_days = int(max_days_match.group(1)) if max_days_match else 0
        
        # 判断是否符合基线标准
        status = (max_days <= 90) if max_days else False
        
        return {
            "check_name": "密码生存期",
            "status": bool(status),
            "details": {
                "密码生存期(天)": max_days
            }
        }
    except Exception as e:
        return {
            "check_name": "密码生存期",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))