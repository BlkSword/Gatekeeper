# 受控文件夹检测
import winreg

def run_check():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows Defender\Windows Defender Exploit Guard\Controlled Folder Access")
        cf_enabled = winreg.QueryValueEx(key, "EnableControlledFolderAccess")[0]
        
        return {
            "check_name": "受控文件夹访问检测",
            "status": cf_enabled == 1
        }
    except:
        return {"check_name": "受控文件夹访问检测", "status": False}
    
if __name__ == "__main__":
    print(run_check())