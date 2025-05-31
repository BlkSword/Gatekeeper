# 驱动器自动播放关闭检测

import winreg

def run_check():
    check_name = "驱动器自动播放关闭检查"
    
    try:
        # 打开注册表项
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer")
        # 获取NoDriveTypeAutoRun值
        auto_run_value, _ = winreg.QueryValueEx(key, "NoDriveTypeAutoRun")
        
        return {
            "check_name": check_name,
            "status": auto_run_value == 0x91  # 0x91表示关闭所有驱动器自动播放
        }
    except FileNotFoundError:
        return {
            "check_name": check_name,
            "status": False
        }
    except Exception as e:
        return {
            "check_name": check_name,
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    print(run_check())