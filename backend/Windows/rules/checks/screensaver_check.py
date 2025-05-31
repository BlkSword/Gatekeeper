# 屏幕保护检测
import winreg

def run_check():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop")
        ss_active = winreg.QueryValueEx(key, "ScreenSaveActive")[0]
        ss_timeout = winreg.QueryValueEx(key, "ScreenSaveTimeOut")[0]
        ss_secure = winreg.QueryValueEx(key, "ScreenSaverIsSecure")[0]
        
        status = ss_active == "1" and int(ss_timeout) <= 900 and ss_secure == "1"
        
        return {
            "check_name": "屏幕保护程序检测",
            "status": status
        }
    except:
        return {"check_name": "屏幕保护程序检测", "status": False}
    
if __name__ == "__main__":
    print(run_check())