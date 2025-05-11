# 动态更新检测
# 检测内容：自动更新设置、补丁安装状态

import platform
import subprocess
import winreg  # 新增注册表模块
from fastapi.logger import logger

def get_auto_update_settings():
    """检测自动更新注册表设置"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
        )
        try:
            no_auto_update, _ = winreg.QueryValueEx(key, "NoAutoUpdate")
            status = "禁用" if no_auto_update == 1 else "启用"  # 明确状态显示
            return {
                "status": status,
                "auto_update_enabled": no_auto_update != 1,
                "registry_status": "found"
            }
        except FileNotFoundError:
            # 键值不存在时默认启用
            return {
                "status": "启用",
                "auto_update_enabled": True,
                "registry_status": "key_not_found"
            }
        finally:
            winreg.CloseKey(key)
    except FileNotFoundError:
        # 注册表路径不存在时默认启用
        return {
            "status": "启用",
            "auto_update_enabled": True,
            "registry_status": "path_not_found"
        }
    except Exception as e:
        logger.error(f"注册表读取异常: {str(e)}")
        return {
            "status": "检测失败",
            "auto_update_enabled": None,
            "error": str(e),
            "registry_status": "error"
        }

def get_detect_update():
    logger.info("开始收集系统更新信息")
    
    # 获取自动更新设置
    auto_update_settings = get_auto_update_settings()

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
        "auto_update_settings": auto_update_settings,
        "updates": update_list
    }