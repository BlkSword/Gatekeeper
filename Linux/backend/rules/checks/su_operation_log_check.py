# 记录SU操作事件到系统日志

import subprocess
import os
import re
import json

def run_check():
    try:
        # 检测PAM配置
        pam_su_conf = subprocess.getoutput("cat /etc/pam.d/su 2>/dev/null")
        # 检查pam是否记录su事件
        pam_audit = re.search(r"pam_(tty_audit|audit)\.so", pam_su_conf)
        
        # 判断是否符合基线标准
        status = bool(pam_audit)
        
        return {
            "check_name": "SU操作日志记录",
            "status": status,
            "actual_value": {
                "pam审计配置": "已配置" if pam_audit else "未配置"
            },
            "baseline": "应通过PAM模块记录su操作的成功/失败事件（如启用pam_audit）"
        }
    except Exception as e:
        return {
            "check_name": "SU操作日志记录",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))