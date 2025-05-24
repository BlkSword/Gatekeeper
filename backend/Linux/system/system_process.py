# 获取服务状态
# 检测内容有：进程和服务状态、已安装程序列表、服务详细信息、关键服务状态、系统配置信息

import subprocess
import psutil
import platform
from datetime import datetime

def get_process_info():
    """获取进程和服务状态信息"""
    
    # 获取关键服务状态
    def get_services():
        try:
            list_output = subprocess.check_output(
                'systemctl list-units --type=service --all --no-pager --no-legend',
                shell=True,
                stderr=subprocess.STDOUT,
                encoding='utf-8'
            )
            services = []
            for line in list_output.split('\n'):
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 4:
                    continue
                svc_name = parts[0]
                active_state = parts[2]
                description = ' '.join(parts[4:]) if len(parts) > 4 else ''

                try:
                    show_output = subprocess.check_output(
                        f'systemctl show {svc_name} --property=Description,MainPID,ExecStart',
                        shell=True,
                        stderr=subprocess.STDOUT,
                        encoding='utf-8'
                    )
                    details = {}
                    for detail_line in show_output.split('\n'):
                        if '=' in detail_line:
                            key, val = detail_line.split('=', 1)
                            details[key.strip()] = val.strip()

                    # 提取可执行路径
                    exec_start = details.get('ExecStart', '')
                    executable_path = exec_start.split()[0] if exec_start else '未知路径'

                    # 提取PID
                    pid_str = details.get('MainPID', '0')
                    pid = int(pid_str) if pid_str.isdigit() else None

                    services.append({
                        "name": svc_name,
                        "display_name": details.get('Description', description),
                        "state": "运行中" if active_state == "active" else "已停止",
                        "pid": pid,
                        "executable_path": executable_path
                    })
                except Exception as e:
                    services.append({
                        "name": svc_name,
                        "display_name": description,
                        "state": "运行中" if active_state == "active" else "已停止",
                        "pid": None,
                        "executable_path": "获取失败"
                    })
            # 过滤系统关键服务
            return [s for s in services if 'systemd' in s.get('name', '') or 'network' in s.get('name', '')]
        except Exception as e:
            return {"error": f"获取服务失败：{str(e)}"}

    # 获取已安装程序列表
    def get_installed_programs():
        try:
            programs = []
            os_release = platform.freedesktop_os_release()
            distro_id = os_release.get('ID', '').lower()

            if distro_id in ['debian', 'ubuntu']:
                dpkg_output = subprocess.check_output(
                    "dpkg-query -W -f='${Package}\t${Version}\t${Installed-Time}\n'",
                    shell=True,
                    stderr=subprocess.STDOUT,
                    encoding='utf-8'
                )
                for line in dpkg_output.split('\n'):
                    line = line.strip()
                    if line:
                        try:
                            name, version, install_time = line.split('\t')
                            install_date = "未知"
                            if install_time.isdigit():
                                install_date = datetime.fromtimestamp(int(install_time)).strftime('%Y-%m-%d')
                            programs.append({
                                "name": name,
                                "version": version,
                                "install_date": install_date
                            })
                        except ValueError:
                            continue
            elif distro_id in ['rhel', 'centos', 'fedora']:
                rpm_output = subprocess.check_output(
                    "rpm -qa --queryformat '%{NAME},%{VERSION},%{INSTALLTIME}\n'",
                    shell=True,
                    stderr=subprocess.STDOUT,
                    encoding='utf-8'
                )
                for line in rpm_output.split('\n'):
                    line = line.strip()
                    if line:
                        try:
                            name, version, install_time = line.split(',', 2)
                            install_date = "未知"
                            if install_time.isdigit():
                                install_date = datetime.fromtimestamp(int(install_time)).strftime('%Y-%m-%d')
                            programs.append({
                                "name": name,
                                "version": version,
                                "install_date": install_date
                            })
                        except ValueError:
                            continue
            else:
                return {"error": f"不支持的Linux发行版: {distro_id}"}
            return programs
        except Exception as e:
            return {"error": f"获取已安装程序失败：{str(e)}"}

    # 获取系统运行时间
    boot_time = psutil.boot_time()
    uptime_seconds = psutil.time.time() - boot_time
    uptime_days = int(uptime_seconds // 86400)
    uptime_hours = int((uptime_seconds % 86400) // 3600)
    uptime_str = f"{uptime_days}天{uptime_hours}小时" if uptime_days > 0 else f"{uptime_hours}小时{int((uptime_seconds % 3600) // 60)}分钟"

    return {
        "critical_services": get_services(),
        "installed_programs": get_installed_programs(),
        "system_uptime": uptime_str
    }