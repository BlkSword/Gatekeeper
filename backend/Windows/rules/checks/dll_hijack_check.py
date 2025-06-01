# DLL劫持检测 
import subprocess
import re
import json

def run_check():
    try:
        dll_path = r"C:\Windows\System32\user32.dll"
        perm_output = subprocess.getoutput(f'icacls "{dll_path}"')
        has_unsafe_perm = re.search(r"(?<!BUILTIN\\Administrators).*:(?=.*W)", perm_output) is not None
        
        return {
            "check_name": "DLL劫持风险检测",
            "status": not has_unsafe_perm
        }
    except:
        return {"check_name": "DLL劫持风险检测", "status": False}
    
if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False)) 