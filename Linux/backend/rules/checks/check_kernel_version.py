# 判断内核版本是否为最新

import subprocess
import json
from packaging.version import Version  

def run_check():
    try:
        current_version = subprocess.getoutput("uname -r").strip()
        current_version_base = current_version.rsplit('.', 1)[0]

        output = subprocess.getoutput("yum list available kernel --quiet")
        lines = output.strip().split('\n')

        available_versions = []
        for line in lines[1:]:
            parts = line.strip().split()
            if len(parts) >= 2:
                version = parts[1]
                available_versions.append(Version(version))  # 直接转换为Version对象

        if not available_versions:
            latest_version = None
        else:
            available_versions.sort(reverse=True)  # 使用Version原生排序
            latest_version = str(available_versions[0])  # 转换回字符串比较

        status = latest_version is not None and current_version_base == latest_version

        return {
            "check_name": "内核版本为最新",
            "status": status
        }

    except Exception as e:
        return {
            "check_name": "内核版本为最新",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))