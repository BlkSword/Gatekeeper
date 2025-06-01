# 自动登录检测
import winreg
import json

def run_check():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon")
        auto_logon = winreg.QueryValueEx(key, "AutoAdminLogon")[0]
        default_pwd = winreg.QueryValueEx(key, "DefaultPassword")[0]
        
        status = auto_logon == "0" and not default_pwd
        
        return {
            "check_name": "自动登录检测",
            "status": status
        }
    except:
        return {"check_name": "自动登录检测", "status": False}
    
if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False)) 