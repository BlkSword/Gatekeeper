# SYN攻击防护检测脚本

import winreg

def run_check():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters")
        syn_value, _ = winreg.QueryValueEx(key, "SynAttackProtect")
        
        return {
            "check_name": "SYN Attack Protection",
            "status": syn_value == 2
        }
    except FileNotFoundError:
        return {"check_name": "SYN Attack Protection", "status": False}
    except Exception:
        return {"check_name": "SYN Attack Protection", "status": False}
    
if __name__ == "__main__":
    print(run_check())