# 系统状态检测
# 检测内容有：系统启动时间，CPU使用率，内存使用情况，磁盘使用情况，负载状态

import psutil
import time
import subprocess
from fastapi.logger import logger

def check_internet():
    logger.info("Start checking system status")
    
    # 获取系统启动时间
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{int(days)}天 {int(hours)}小时 {int(minutes)}分钟"
    
    # 获取CPU使用率
    cpu_cores = psutil.cpu_count(logical=True)
    per_cpu_usage = psutil.cpu_percent(percpu=True)
    cpu_percent_total = psutil.cpu_percent()
    
    # 获取内存使用情况
    memory = psutil.virtual_memory()
    
    # 获取磁盘使用情况
    disks = []
    total_disk_space = 0
    total_disk_used = 0
    
    for partition in psutil.disk_partitions():
        if partition.fstype in ['tmpfs', 'devtmpfs']:
            continue
            
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            if usage.total == 0:
                continue
                
            disks.append({
                "drive": partition.device,
                "total": f"{usage.total / (1024**3):.2f} GB",
                "used": f"{usage.used / (1024**3):.2f} GB",
                "free": f"{usage.free / (1024**3):.2f} GB",
                "percent": f"{usage.percent}%"
            })
            total_disk_space += usage.total
            total_disk_used += usage.used
        except PermissionError:
            continue
    
    # 计算总磁盘使用率
    total_disk_percent = (total_disk_used / total_disk_space * 100) if total_disk_space > 0 else 0

    # 新增：获取系统负载
    def _get_system_load():
        try:
            output = subprocess.check_output(["uptime"], stderr=subprocess.STDOUT, shell=True).decode()
            if "load average" in output:
                load_avg = output.split("load average:")[1].strip().split(',')[2].strip()
                return load_avg
            return "0.0"
        except Exception as e:
            logger.error(f"获取系统负载失败: {e}")
            return "0.0"

    # 用户信息检测
    current_user = psutil.users()[0].name if psutil.users() else "未知用户"

    # 网络状态检测
    def _check_internet_connection():
        try:
            subprocess.check_output(["ping", "-c", "1", "8.8.8.8"], timeout=2)
            return "已联网"
        except:
            return "未联网"

    result = {
        "system_load": f"{_get_system_load()}%",  # 使用uptime的5分钟负载
        "cpu_usage": f"{cpu_percent_total}%",
        "cpu_cores": cpu_cores,
        "per_cpu_usage": [f"{core}%" for core in per_cpu_usage],
        "memory": {
            "total": f"{memory.total / (1024**3):.2f} GB",
            "used": f"{memory.used / (1024**3):.2f} GB",
            "percent": f"{memory.percent}%"
        },
        "disks": disks,
        "disk_total": {
            "total": f"{total_disk_space / (1024**3):.2f} GB",
            "used": f"{total_disk_used / (1024**3):.2f} GB",
            "percent": f"{total_disk_percent:.1f}%"
        },
        "uptime": uptime,
        "network_status": _check_internet_connection(),
        "current_user": current_user
    }
    
    logger.info(f"System status checked. CPU Usage: {cpu_percent_total}% Load: {result['system_load']}")
    return result