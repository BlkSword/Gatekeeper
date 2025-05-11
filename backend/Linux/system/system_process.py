# 获取服务状态
# 检测内容有：进程和服务状态、已安装程序列表、服务详细信息、关键服务状态、系统配置信息

import subprocess
import psutil
import platform

def get_process_info():
    """获取进程和服务状态信息"""
    # 获取关键服务状态（Linux适配）
    def get_services():
        try:
            # 获取所有服务的基本信息（包括状态）
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
                # 解析 systemctl 输出格式（示例行："apache2.service   loaded active running The Apache HTTP Server"）
                parts = line.split()
                if len(parts) < 4:
                    continue
                svc_name = parts[0]
                loaded_state = parts[1]
                active_state = parts[2]
                sub_state = parts[3]
                description = ' '.join(parts[4:]) if len(parts) > 4 else ''

                # 获取服务详细信息（启动类型、依赖等）
                try:
                    show_output = subprocess.check_output(
                        f'systemctl show {svc_name} --property=UnitFileState,Requires,Description',
                        shell=True,
                        stderr=subprocess.STDOUT,
                        encoding='utf-8'
                    )
                    details = {}
                    for detail_line in show_output.split('\n'):
                        if '=' in detail_line:
                            key, val = detail_line.split('=', 1)
                            details[key] = val.strip()
                    
                    services.append({
                        "name": svc_name,
                        "display_name": details.get('Description', description),
                        "state": "运行中" if active_state == "active" else "已停止",
                        "type": "服务",
                        "start_type": {
                            "enabled": "自动",
                            "disabled": "手动",
                            "static": "静态"
                        }.get(details.get('UnitFileState', 'unknown'), "未知"),
                        "dependencies": details.get('Requires', '').split(' '),
                        "description": details.get('Description', description)
                    })
                except Exception as e:
                    services.append({
                        "name": svc_name,
                        "display_name": description,
                        "state": "已停止" if active_state != "active" else "运行中",
                        "type": "服务",
                        "start_type": "未知",
                        "dependencies": [],
                        "description": f"获取详细信息失败：{str(e)}"
                    })
            
            # 过滤包含"关键"或用户指定关键词的服务（示例过滤条件）
            return [s for s in services if '关键' in s.get('display_name', '') or '重要' in s.get('display_name', '')]
        except Exception as e:
            return {"error": f"获取服务失败：{str(e)}"}

    # 获取已安装程序列表（Linux适配）
    def get_installed_programs():
        try:
            programs = []
            # 检测包管理器类型（支持 dpkg 和 rpm）- 使用 freedesktop_os_release 替代已弃用的 linux_distribution
            try:
                os_release = platform.freedesktop_os_release()
                distro_id = os_release.get('ID', '').lower()  # 从 /etc/os-release 获取发行版ID
            except AttributeError:
                return {"error": "不支持的Python版本，请使用3.10或更高版本"}

            if distro_id in ['debian', 'ubuntu']:
                # Debian/Ubuntu 系使用 dpkg
                dpkg_output = subprocess.check_output(
                    'dpkg -l | awk \'NR>5 {print $2","$3","$4}\'',  # 跳过头部，提取名称、版本、供应商
                    shell=True,
                    stderr=subprocess.STDOUT,
                    encoding='utf-8'
                )
                for line in dpkg_output.split('\n'):
                    line = line.strip()
                    if line:
                        name, version, publisher = line.split(',', 2)
                        programs.append({
                            "name": name,
                            "version": version,
                            "publisher": publisher if publisher else "未知"
                        })
            elif distro_id in ['rhel', 'centos', 'fedora']:  # 注意：redhat 系的 ID 通常是 'rhel' 而非 'redhat'
                # RedHat 系使用 rpm
                rpm_output = subprocess.check_output(
                    'rpm -qa --queryformat \'%{NAME},%{VERSION},%{VENDOR}\\n\'',
                    shell=True,
                    stderr=subprocess.STDOUT,
                    encoding='utf-8'
                )
                for line in rpm_output.split('\n'):
                    line = line.strip()
                    if line:
                        name, version, publisher = line.split(',', 2)
                        programs.append({
                            "name": name,
                            "version": version,
                            "publisher": publisher if publisher else "未知"
                        })
            else:
                return {"error": f"不支持的Linux发行版: {distro_id}"}
            
            return programs
        except Exception as e:
            return {"error": f"获取已安装程序失败：{str(e)}"}

    # 系统运行时间（调整格式化）
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




