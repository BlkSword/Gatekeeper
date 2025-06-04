# 密码复杂度检测

import subprocess
import re
import json
import os

def run_check():
    try:
        # 获取密码复杂度配置
        pwquality = subprocess.getoutput("cat /etc/security/pwquality.conf 2>/dev/null")
        
        # 解析最小长度和最少字符类型
        minlen_match = re.search(r"minlen\s*=\s*(\d+)", pwquality)
        minclass_match = re.search(r"minclass\s*=\s*(\d+)", pwquality)
        
        minlen = int(minlen_match.group(1)) if minlen_match else 0
        minclass = int(minclass_match.group(1)) if minclass_match else 0
        
        # 判断是否符合基线标准
        status = (minlen >= 8) and (minclass >= 4)
        
        return {
            "check_name": "密码复杂度",
            "status": bool(status),
            "details": {
                "最小长度": minlen,
                "最少字符类型": minclass
            }
        }
    except Exception as e:
        return {
            "check_name": "密码复杂度",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))