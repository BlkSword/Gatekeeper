# 管理员账号重命名检测
import subprocess

def run_check():
    try:
        user_output = subprocess.getoutput('net user')
        return {
            "check_name": "默认管理员账号重命名",
            "status": "Administrator" not in user_output
        }
    except Exception as e:
        return {
            "check_name": "默认管理员账号重命名",
            "status": False,
            "error": str(e)
        }
    
if __name__ == "__main__":
    print(run_check())