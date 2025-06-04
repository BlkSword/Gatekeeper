# 匿名FTP检测

import subprocess
import re
import json

def run_check():
    try:
        # 检查FTP服务安装状态
        ftp_installed = "vsftpd" in subprocess.getoutput("dpkg -l | grep vsftpd 2>/dev/null") or \
                       "vsftpd" in subprocess.getoutput("rpm -qa | grep vsftpd 2>/dev/null")
        
        if not ftp_installed:
            return {
                "check_name": "匿名FTP登录检测",
                "status": True  # 未安装即合规
            }
        
        # 检查vsftpd配置
        vsftpd_conf = subprocess.getoutput("cat /etc/vsftpd/vsftpd.conf 2>/dev/null")
        anonymous_enable = re.search(r"^anonymous_enable\s*=\s*(\w+)", vsftpd_conf, re.MULTILINE)
        
        # 判断配置是否合规
        status = (anonymous_enable and anonymous_enable.group(1).upper() == "NO")
        
        return {
            "check_name": "匿名FTP登录检测",
            "status": bool(status)
        }
    except Exception as e:
        return {
            "check_name": "匿名FTP登录检测",
            "status": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False))