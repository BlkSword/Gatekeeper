# 检测补丁信息
# 检测内容有：操作系统信息、已安装的更新补丁

import platform
import subprocess
from fastapi.logger import logger

def get_rules_patch():
    logger.info("Start collecting system information")
    # 获取操作系统信息
    os_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "win32_edition": platform.win32_edition() if hasattr(platform, 'win32_edition') else None,
        "service_pack": platform.win32_ver()[2] if platform.system() == 'Windows' else None,
        "build_number": platform.win32_ver()[1] if platform.system() == 'Windows' else None
    }

    # 获取已安装的更新补丁
    try:
        updates = subprocess.check_output(
            'wmic qfe get Caption,Description,HotFixID,InstalledOn /format:csv',
            shell=True,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        ).split('\n')
        
        update_list = []
        for line in updates[1:]:
            if line.strip():
                parts = line.split(',')
                if len(parts) >= 5:
                    update_list.append({
                        "kb_number": parts[1].strip(),
                        "description": parts[2].strip(),
                        "install_date": parts[3].strip(),
                        "caption": parts[4].strip()
                    })
    except Exception as e:
        update_list = [{"error": str(e)}]

    return {
        # 保留原有字段
        "os_information": os_info,
        "windows_version": platform.win32_ver(),
        "updates": update_list
    }