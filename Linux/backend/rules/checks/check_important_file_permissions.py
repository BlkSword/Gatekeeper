# 重要文件权限检测

import os
import subprocess
import json

def run_check():
    try:
        important_files = ["/etc/passwd", "/etc/shadow", "/etc/group"]
        all_compliant = True  # 标记是否全部符合

        for file in important_files:
            # 根据文件类型定义权限基线
            if file == "/etc/shadow":
                baseline_perm = "600"
            else:
                baseline_perm = "644"
            # 获取实际权限
            perm = subprocess.getoutput(f"stat -c %a {file} 2>/dev/null") or "未配置"
            # 判断是否符合基线
            if perm != baseline_perm:
                all_compliant = False
                break  # 只要有一个不符合就终止检查

        return {
            "check_name": "重要文件权限检测（/etc/passwd /etc/shadow /etc/group）",
            "status": all_compliant
        }
    except Exception as e:
        return {
            "check_name": "重要文件权限检测（/etc/passwd /etc/shadow /etc/group）",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))