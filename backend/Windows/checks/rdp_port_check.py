# 远程桌面端口检测脚本

import winreg

def run_check():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp")
        port, _ = winreg.QueryValueEx(key, "PortNumber")
        
        return {
            "check_name": "Remote Desktop Port",
            "status": port != 3389
        }
    except Exception:
        return {"check_name": "Remote Desktop Port", "status": False}
    
if __name__ == "__main__":
    print(run_check())