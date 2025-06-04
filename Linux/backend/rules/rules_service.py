# 服务相关检测
# 检测内容：关闭不必要服务（Telnet、NFS、RPC 等）、禁止匿名 FTP 登录

import platform
import subprocess
import re
import os

def get_rules_service():
    # 获取基础信息
    hostname = platform.node()
    domain = subprocess.getoutput("dnsdomainname").strip() or "N/A"

    # 关闭不必要服务检测（Telnet、NFS、RPC 等）
    def check_unnecessary_services():
        try:
            # 检测服务安装状态（Debian系用dpkg，RHEL系用rpm）
            def is_service_installed(service):
                return (f"{service}" in subprocess.getoutput(f"dpkg -l | grep {service} 2>/dev/null") or 
                        f"{service}" in subprocess.getoutput(f"rpm -qa | grep {service} 2>/dev/null"))
            
            # 检测服务运行状态
            def is_service_active(service):
                status = subprocess.getoutput(f"systemctl is-active {service} 2>/dev/null")
                return status == "active"

            # 目标服务列表
            target_services = ["telnet", "nfs", "rpcbind"]
            service_info = []
            
            for service in target_services:
                installed = is_service_installed(service)
                active = is_service_active(service) if installed else False
                service_info.append({
                    "服务名称": service,
                    "是否安装": "已安装" if installed else "未安装",
                    "是否运行": "运行中" if active else "未运行"
                })

            return {
                "实际值": service_info,
                "基线标准": "应卸载或禁用不必要服务（如Telnet、NFS、RPC），确保未安装或未运行",
                "是否符合": "符合" if not any(svc["是否安装"] == "已安装" and svc["是否运行"] == "运行中" for svc in service_info) else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 禁止匿名 FTP 登录检测
    def check_anonymous_ftp():
        try:
            # 检查vsftpd配置（常见FTP服务）
            vsftpd_conf = subprocess.getoutput("cat /etc/vsftpd/vsftpd.conf 2>/dev/null")
            anonymous_enable = re.search(r"^anonymous_enable\s*=\s*(\w+)", vsftpd_conf, re.MULTILINE)
            
            # 检测FTP服务是否安装
            ftp_installed = "vsftpd" in subprocess.getoutput("dpkg -l | grep vsftpd 2>/dev/null") or \
                            "vsftpd" in subprocess.getoutput("rpm -qa | grep vsftpd 2>/dev/null")

            return {
                "实际值": {
                    "匿名登录配置": anonymous_enable.group(1) if anonymous_enable else "未配置",
                    "FTP服务是否安装": "已安装" if ftp_installed else "未安装"
                },
                "基线标准": "若安装FTP服务，应禁止匿名登录（anonymous_enable=NO）",
                "是否符合": "符合" if (not ftp_installed) or (anonymous_enable and anonymous_enable.group(1) == "NO") else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合安全策略检测
    def check_security_policy():
        try:
            return {
                "unnecessary_services": check_unnecessary_services(),
                "anonymous_ftp": check_anonymous_ftp()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data