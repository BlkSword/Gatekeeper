# 密码复杂性策略检测
import subprocess
import os

def run_check():
    try:
        temp_path = os.path.join(os.environ['TEMP'], 'secpol.cfg')
        result = subprocess.getoutput(f'secedit /export /cfg {temp_path} && find "PasswordComplexity" {temp_path}')
        return {
            "check_name": "密码复杂性策略",
            "status": "1" in result
        }
    except Exception as e:
        return {
            "check_name": "密码复杂性策略",
            "status": False,
            "error": str(e)
        }
    
if __name__ == "__main__":
    print(run_check())