# Wheel 组 SU 限制检测

import subprocess
import re
import json

def run_check():
    try:
        # 读取 PAM 配置
        su_config = subprocess.getoutput("cat /etc/pam.d/su 2>/dev/null")
        # 检查 wheel 组限制是否启用
        wheel_enabled = re.search(
            r"^auth\s+required\s+pam_wheel\.so\s+use_uid", 
            su_config, 
            re.MULTILINE
        ) is not None
        return {
            "check_name": "Wheel 组 SU 限制",
            "status": wheel_enabled,
            "details": {"configured": "已启用" if wheel_enabled else "未启用"}
        }
    except Exception as e:
        return {
            "check_name": "Wheel 组 SU 限制",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))