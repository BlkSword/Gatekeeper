# 记录登录失败事件到系统日志

import subprocess
import os
import re
import json

def run_check():
    try:
        # 检测rsyslog配置
        rsyslog_conf = subprocess.getoutput("cat /etc/rsyslog.conf 2>/dev/null")
        # 匹配auth相关日志目标
        log_target = re.search(r"^(auth|authpriv)\.\*\s+(/var/log/(auth\.log|secure))", rsyslog_conf, re.MULTILINE)
        
        # 检测日志文件是否存在且可写
        log_file = log_target.group(2) if log_target else ""
        log_writable = os.access(log_file, os.W_OK) if log_file else False

        # 判断是否符合基线标准
        status = bool(log_target and log_writable)
        
        return {
            "check_name": "登录失败日志记录",
            "status": status,
            "actual_value": {
                "配置路径": log_target.group(0) if log_target else "未配置",
                "日志文件可写性": "可写" if log_writable else "不可写"
            },
            "baseline": "应配置记录登录失败事件到系统日志（如/var/log/auth.log或/var/log/secure），且日志文件可写"
        }
    except Exception as e:
        return {
            "check_name": "登录失败日志记录",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))