# 服务相关检测

import platform
import subprocess
import re
import socket
import winreg  # 用于注册表操作

def get_rules_service():
    # 获取基础信息
    hostname = platform.node()
    domain = socket.getfqdn().split('.', 1)[1] if '.' in socket.getfqdn() else "N/A"

    # 检测不必要服务（TELNET、RemoteRegistry、SMTP等）
    def check_unnecessary_services():
        target_services = ["TELNET", "RemoteRegistry", "SMTP"]  # 目标检测服务列表
        service_results = {}
        
        for service in target_services:
            try:
                # 使用PowerShell获取服务启动类型（Disabled表示禁用）
                ps_cmd = f"Get-Service -Name {service} -ErrorAction SilentlyContinue | Select-Object StartType"
                output = subprocess.getoutput(f'powershell "{ps_cmd}"')
                
                start_type = re.search(r"StartType\s+(\w+)", output).group(1) if re.search(r"StartType", output) else "未找到服务"
                actual_value = "已禁用" if start_type == "Disabled" else f"未禁用（启动类型：{start_type}）"
                
                service_results[service] = {
                    "实际值": actual_value,
                    "基线标准": "应禁用TELNET、RemoteRegistry、SMTP等不必要服务（启动类型为Disabled）",
                    "是否符合": "符合" if start_type == "Disabled" else "不符合"
                }
            except Exception as e:
                service_results[service] = {"error": f"检测失败：{str(e)}"}
        
        return service_results

    # 检测所有驱动器自动播放关闭状态（基于注册表）
    def check_autoplay_disabled():
        try:
            # 打开自动播放策略注册表项
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer")
            # 获取NoDriveTypeAutoRun值（DWORD类型，0x91表示关闭所有驱动器自动播放）
            auto_run_value, _ = winreg.QueryValueEx(key, "NoDriveTypeAutoRun")
            
            return {
                "实际值": f"0x{auto_run_value:X}",
                "基线标准": "应关闭所有驱动器自动播放（注册表值应为0x91）",
                "是否符合": "符合" if auto_run_value == 0x91 else "不符合"
            }
        except FileNotFoundError:
            return {
                "实际值": "未配置",
                "基线标准": "应关闭所有驱动器自动播放（注册表值应为0x91）",
                "是否符合": "不符合"
            }
        except Exception as e:
            return {"error": f"检测失败：{str(e)}"}

    # 整合安全策略检测
    def check_security_policy():
        try:
            return {
                "unnecessary_services": check_unnecessary_services(),
                "autoplay_disabled": check_autoplay_disabled()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data