# 系统状态检测
# 检测内容有：系统启动时间，CPU使用率，内存使用情况，磁盘使用情况，负载状态

import psutil
from fastapi.logger import logger
import threading

_cpu_usage_history = []
_history_lock = threading.Lock()

def check_system_status():
    logger.info("Start checking system status")

    # 获取 CPU 使用率
    cpu_percent_total = psutil.cpu_percent(interval=1)

    # 更新 CPU 使用率历史记录
    global _cpu_usage_history
    with _history_lock:
        _cpu_usage_history.append(cpu_percent_total)
        if len(_cpu_usage_history) > 3:
            _cpu_usage_history.pop(0)

        # 计算系统负载
        system_load = sum(_cpu_usage_history) / len(_cpu_usage_history) if _cpu_usage_history else 0.0

    # 获取内存使用情况
    memory = psutil.virtual_memory()
    total_disk_space = 0
    total_disk_used = 0

    # 获取磁盘信息
    for partition in psutil.disk_partitions():
        if 'fixed' in partition.opts:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                total_disk_space += usage.total
                total_disk_used += usage.used
            except PermissionError:
                continue

    # 计算总磁盘使用率
    total_disk_percent = (total_disk_used / total_disk_space * 100) if total_disk_space > 0 else 0

    result = {
        "system_load": f"{system_load:.1f}%",  
        "cpu_usage": f"{cpu_percent_total}%",
        "memory": {
            "total": f"{memory.total / (1024**3):.2f} GB",
            "used": f"{memory.used / (1024**3):.2f} GB",
            "percent": f"{memory.percent}%"
        },
        "disk_total": {
            "total": f"{total_disk_space / (1024**3):.2f} GB",
            "used": f"{total_disk_used / (1024**3):.2f} GB",
            "percent": f"{total_disk_percent:.1f}%"
        },
    }

    logger.info(f"System status checked. CPU Usage: {cpu_percent_total}%")
    return result