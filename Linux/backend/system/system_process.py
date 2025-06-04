# 获取进程和服务状态信息
# 检测内容有：关键服务状态（显示名称/状态/PID/可执行路径）、已安装程序列表

import subprocess
from fastapi import logger
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
                    if current_svc.get('display_name'):
                        services.append(current_svc)
                    current_svc = {'name': line.split(':', 1)[1].strip()}
                elif line.startswith('DISPLAY_NAME'):
                    current_svc['display_name'] = line.split(':', 1)[1].strip()
                elif line.startswith('STATE'):
                    state = line.split(':', 1)[1].strip().split()[0]
                    current_svc['state'] = '运行中' if state == '4' else '已停止'
                elif line.startswith('WIN32_PID'):
                    pid_str = line.split(':', 1)[1].strip()
                    current_svc['pid'] = int(pid_str) if pid_str.isdigit() else None
            
            # 获取服务可执行文件路径
            for svc in services:
                try:
                    qc_output = subprocess.check_output(
                        f'sc qc "{svc["name"]}"',
                        shell=True,
                        stderr=subprocess.STDOUT,
                        encoding='gbk'
                    )
                    for qc_line in qc_output.split('\n'):
                        qc_line = qc_line.strip()
                        if qc_line.startswith('BINARY_PATH_NAME'):
                            path = qc_line.split(':', 1)[1].strip()
                            svc['executable_path'] = path
                            break
                    else:
                        svc['executable_path'] = '未知路径'
                except Exception as e:
                    svc['executable_path'] = '获取失败'
            
            return [s for s in services if s.get('display_name') and 'Windows' in s.get('display_name', '')]
        except Exception as e:
            return {"error": str(e)}

    # 获取已安装程序列表
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
                            install_date = "未知"
                            try:
                                install_date = winreg.QueryValueEx(subkey, 'InstallDate')[0]
                            except OSError:
                                pass
                                
                            programs.append({
                                "name": name,
                                "version": version,
                                "install_date": install_date  
                            })
                        except OSError:
                            continue
            return programs
        except Exception as e:
            logger.error(f"Failed to get installed programs: {str(e)}")
            return {"error": str(e)}

    return {
        "critical_services": get_services(),
        "installed_programs": get_installed_programs()
    }