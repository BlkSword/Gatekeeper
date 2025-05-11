# 系统状态检测
# 检测内容有：系统启动时间，CPU使用率，内存使用情况，磁盘使用情况，
# 网络连接状态，用户信息

import psutil
import time
import subprocess
from fastapi.logger import logger


def check_system_status():  # 修正1：函数重命名
    logger.info("Start checking system status")
    # 获取系统启动时间（时间戳）
    boot_time = psutil.boot_time()
    # 计算运行时间（秒）
    uptime_seconds = time.time() - boot_time
    # 将秒转换为天、小时、分钟
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{int(days)}天 {int(hours)}小时 {int(minutes)}分钟"
    # 获取 CPU 使用率（添加interval参数确保采样准确）
    cpu_cores = psutil.cpu_count(logical=True)  
    per_cpu_usage = psutil.cpu_percent(interval=1, percpu=True)  # 修正2：添加interval参数
    cpu_percent_total = psutil.cpu_percent(interval=1)  # 修正2：添加interval参数
    
    # 获取内存使用情况（单位转换为GB）
    memory = psutil.virtual_memory()
    # 获取磁盘使用情况
    disks = []
    total_disk_space = 0
    total_disk_used = 0
    
    # 获取所有磁盘分区信息
    for partition in psutil.disk_partitions():
        if 'fixed' in partition.opts:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "drive": partition.device,
                    "total": f"{usage.total / (1024**3):.2f} GB",  # 明确单位转换说明
                    "used": f"{usage.used / (1024**3):.2f} GB",
                    "free": f"{usage.free / (1024**3):.2f} GB",
                    "percent": f"{usage.percent}%"
                })
                total_disk_space += usage.total
                total_disk_used += usage.used
            except PermissionError:
                continue
    
    # 计算总磁盘使用率（防止除零错误）
    total_disk_percent = (total_disk_used / total_disk_space * 100) if total_disk_space > 0 else 0

    # 用户信息检测
    current_user = psutil.users()[0].name if psutil.users() else "未知用户"

    
    def _check_internet_connection():
        try:
            subprocess.check_output(["ping", "-n", "1", "8.8.8.8"], timeout=2)
            return "已联网"
        except:
            return "未联网"

    result = {
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
    logger.info(f"System status checked. CPU Usage: {cpu_percent_total}%")
    return result