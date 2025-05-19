# 获取进程和服务状态信息
# 检测内容有：进程和服务状态信息、已安装的程序列表、进程详细信息、服务详细信息、
# 关键服务状态、系统配置信息

import subprocess
from fastapi import logger
import psutil
import winreg

def get_process_info():
    """获取进程和服务状态信息"""
    # 获取关键服务状态
    def get_services():
        try:
            output = subprocess.check_output(
                'sc queryex type= service state= all', 
                shell=True,
                stderr=subprocess.STDOUT,
                encoding='gbk'
            )
            
            services = []
            current_svc = {}
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('SERVICE_NAME'):
                    if current_svc.get('name'):
                        services.append(current_svc)
                    current_svc = {'name': line.split(':', 1)[1].strip()}
                elif line.startswith('DISPLAY_NAME'):
                    current_svc['display_name'] = line.split(':', 1)[1].strip()
                elif line.startswith('STATE'):
                    state = line.split(':', 1)[1].strip().split()[0]
                    current_svc['state'] = '运行中' if state == '4' else '已停止'
                elif line.startswith('SERVICE_TYPE'):
                    service_type = line.split(':', 1)[1].strip().split()[0]
                    current_svc['type'] = '内核驱动' if service_type == '1' else '用户进程'
                elif line.startswith('START_TYPE'):
                    start_type = line.split(':', 1)[1].strip().split()[0]
                    current_svc['start_type'] = {
                        '2': '自动',
                        '3': '手动',
                        '4': '禁用'
                    }.get(start_type, '未知')
        
            # 获取服务描述和依赖关系
            for svc in services:
                try:
                    qc_output = subprocess.check_output(
                        f'sc qc "{svc["name"]}"',
                        shell=True,
                        stderr=subprocess.STDOUT,
                        encoding='gbk'
                    )
                    svc['description'] = '无描述'
                    svc['dependencies'] = []
                    for qc_line in qc_output.split('\n'):
                        qc_line = qc_line.strip()
                        if qc_line.startswith('DESCRIPTION'):
                            parts = qc_line.split(':', 1)
                            if len(parts) > 1:
                                stripped = parts[1].strip()
                                svc['description'] = stripped if stripped else '无描述'
                        elif qc_line.startswith('DEPENDENCIES'):
                            deps = qc_line.split(':', 1)[1].strip()
                            svc['dependencies'] = [d.strip() for d in deps.split(',') if d.strip()]
                except Exception as e:
                    svc['description'] = '获取失败'
                    svc['dependencies'] = []
        
            return [s for s in services if s.get('name') and 'Windows' in s.get('display_name', '')]
        except Exception as e:
            return {"error": str(e)}

    # 获取已安装程序列表
    # 在get_installed_programs函数中
    def get_installed_programs():
        try:
            programs = []
            reg_paths = [
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
                r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
            ]
            
            for path in reg_paths:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            name = winreg.QueryValueEx(subkey, 'DisplayName')[0]
                            version = winreg.QueryValueEx(subkey, 'DisplayVersion')[0]
                            programs.append({
                                "name": name,
                                "version": version,
                                "publisher": winreg.QueryValueEx(subkey, 'Publisher')[0] if winreg.QueryValueEx(subkey, 'Publisher')[0] else "未知"
                            })
                        except OSError:
                            continue
            return programs
        except Exception as e:
            logger.error(f"Failed to get installed programs: {str(e)}")
            return {"error": str(e)}

    
    
    return {
        "critical_services": get_services(),
        "installed_programs": get_installed_programs(),
        "system_uptime": f"{psutil.boot_time():.2f} seconds"
    }




