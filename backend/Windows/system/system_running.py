# 获取正在运行的进程信息
# 包括应用程序和后台进程，进程名称、进程ID（PID）、
# CPU/内存占用率、进程路径、启动用户及权限等级（管理员/标准用户）

import time
import win32api
import win32con
import win32security
from psutil import process_iter, Process
from psutil._common import AccessDenied

def is_admin_process(pid):
    """检查指定PID的进程是否以管理员权限运行"""
    try:
        # 打开进程句柄（需要查询信息权限）
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
        # 打开进程令牌
        htoken = win32security.OpenProcessToken(hproc, win32security.TOKEN_QUERY)
        # 创建管理员组的已知SID
        admin_sid = win32security.CreateWellKnownSid(win32security.WinBuiltinAdministratorsSid, None)
        # 检查令牌是否属于管理员组
        is_admin = win32security.CheckTokenMembership(htoken, admin_sid)
        return is_admin
    except Exception:
        return False
    finally:
        # 清理资源
        try: win32api.CloseHandle(htoken)
        except: pass
        try: win32api.CloseHandle(hproc)
        except: pass

def get_running_processes():
    try:
        # 预收集CPU使用率数据（解决首次获取为0的问题）
        for proc in process_iter():
            try: proc.cpu_percent(interval=0.1)
            except (AccessDenied, Exception): pass
        time.sleep(0.1)  # 等待数据稳定

        applications = []
        background_processes = []
        
        for proc in process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'create_time']):
            if proc.info['name'] not in ['System Idle Process', 'System']:
                p = proc.info
                process_info = {
                    "pid": p['pid'],
                    "name": p['name'],
                    "cpu_usage": f"{p['cpu_percent']:.2f}%",
                    "memory_mb": f"{p['memory_info'].rss / (1024**2):.2f} MB",
                    "status": p['status'],
                    "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(p['create_time'])),
                    "exe_path": proc.exe(),
                    "user": "N/A",
                    "privilege_level": "标准用户"
                }
                
                try:
                    # 获取进程用户信息
                    username = proc.username()
                    process_info['user'] = username.split('\\')[-1]
                    
                    # 直接通过PID检查管理员权限（修正原逻辑错误）
                    process_info['privilege_level'] = "管理员" if is_admin_process(proc.pid) else "标准用户"
                except (AccessDenied, win32security.error):
                    pass

                # 分类逻辑保持不变
                if process_info['exe_path'] and \
                   ('Program Files' in process_info['exe_path'] or 
                    'WindowsApps' in process_info['exe_path']):
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



