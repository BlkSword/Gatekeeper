# 危险文件检测

import os
import subprocess
import json

def run_check():
    try:
        dangerous_files = [".rhosts", "hosts.equiv"]
        existing_files = []
        for file in dangerous_files:
            # 检查用户家目录
            home_dirs = subprocess.getoutput("getent passwd | awk -F: '{print $6}'").split()
            for home in home_dirs:
                file_path = os.path.join(home, file)
                if os.path.exists(file_path):
                    existing_files.append(file_path)
            # 检查根目录
            root_path = os.path.join("/", file)
            if os.path.exists(root_path):
                existing_files.append(root_path)
        # 判断是否符合（无危险文件）
        return {
            "check_name": "危险文件检测（.rhosts、hosts.equiv）",
            "status": not bool(existing_files)  # 无文件时返回 True
        }
    except Exception as e:
        return {
            "check_name": "危险文件检测（.rhosts、hosts.equiv）",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))