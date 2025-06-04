import psutil
import time

def check_baseline_status():
    # 获取CPU使用率（1秒间隔采样）
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # 获取内存使用率
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    
    # 获取磁盘IO和网络流量（1秒间隔采样）
    disk_io_start = psutil.disk_io_counters()
    net_io_start = psutil.net_io_counters()
    time.sleep(1)
    disk_io_end = psutil.disk_io_counters()
    net_io_end = psutil.net_io_counters()
    
    # 计算磁盘IO（KB/s）
    disk_io = (disk_io_end.read_bytes - disk_io_start.read_bytes + 
              disk_io_end.write_bytes - disk_io_start.write_bytes) // 1024
    
    # 计算网络流量（KB/s）
    network_traffic = (net_io_end.bytes_sent - net_io_start.bytes_sent + 
                      net_io_end.bytes_recv - net_io_start.bytes_recv) // 1024
    
    return {
        "cpu_usage": round(cpu_usage, 1),
        "memory_usage": round(memory_usage, 1),
        "disk_io": disk_io,
        "network_traffic": network_traffic
    }

# if  __name__ == "__main__":
#     print(check_baseline_status())