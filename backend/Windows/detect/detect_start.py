# 服务启动检测
# 检测内容：Windows防火墙、Windows Update、Telnet、Remote Registry、Print Spooler

import subprocess
import json

def get_detect_start():
    service_names = [
        'MpsSvc',        # Windows防火墙
        'wuauserv',      # Windows Update
        'Telnet',        # Telnet
        'RemoteRegistry',# Remote Registry
        'Spooler'        # Print Spooler
    ]
    
    result = {}
    for service in service_names:
        try:
            # 执行PowerShell命令获取服务信息
            ps_command = f"Get-Service -Name {service} | Select-Object Name,DisplayName,Status,StartType | ConvertTo-Json"
            output = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True, shell=True)
            
            if output.returncode == 0:
                service_info = json.loads(output.stdout)
                result[service] = {
                    "display_name": service_info['DisplayName'],
                    "startup_type": service_info['StartType'],
                    "status": "运行中" if service_info['Status'] == 'Running' else "已停止"
                }
            else:
                result[service] = {
                    "error": f"服务检测失败: {output.stderr.strip()}"
                }
        except Exception as e:
            result[service] = {
                "error": f"服务检测异常: {str(e)}"
            }
    return result