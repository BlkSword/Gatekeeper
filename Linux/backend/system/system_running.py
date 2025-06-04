# 获取进程信息
# 包括进程名称、PID、资源占用率、路径、用户权限、进程路径、启动用户及权限等级、进程详细信息

import time
import psutil
from psutil import process_iter, AccessDenied

def is_admin_user(uid):
    # Linux 下 UID 为 0 表示 root 用户（管理员权限）
    return uid == 0

def get_running_processes():
    try:
        applications = []
        background_processes = []
        
        for proc in process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'create_time']):
            if proc.info['name'] not in ['kthreadd', 'swapper/0']:  # Linux 核心进程过滤
                p = proc.info
                try:
                    exe_path = proc.exe()  # Linux 下可能返回空（如内核线程）
                except AccessDenied:
                    exe_path = "N/A"

                process_info = {
                    "pid": p['pid'],
                    "name": p['name'],
                    "cpu_usage": f"{p['cpu_percent']:.2f}%",
                    "memory_mb": f"{p['memory_info'].rss / (1024**2):.2f} MB",
                    "status": p['status'],
                    "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(p['create_time'])),
                    "exe_path": exe_path,
                    "user": "N/A",
                    "privilege_level": "标准用户"
                }
                
                try:
                    # Linux 直接获取用户名（无需处理反斜杠）
                    username = proc.username()
                    process_info['user'] = username
                    
                    # 获取实际用户 ID（real UID）判断权限
                    uid = proc.uids().real
                    process_info['privilege_level'] = "管理员" if is_admin_user(uid) else "标准用户"
                except (AccessDenied, psutil.Error):
                    pass

                # Linux 应用程序常见路径调整（示例路径，可根据实际需求扩展）
                if process_info['exe_path'] and \
                   ('/usr/bin/' in process_info['exe_path'] or 
                    '/usr/local/bin/' in process_info['exe_path'] or 
                    '/opt/' in process_info['exe_path']):
                    applications.append(process_info)
                else:
                    background_processes.append(process_info)
        return {
            "applications": applications,
            "background_processes": background_processes,
            "total_applications": len(applications),
            "total_background": len(background_processes),
            "total_processes": len(applications) + len(background_processes)
        }
    except Exception as e:
        return {"error": str(e)}



