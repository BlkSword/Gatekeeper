# 网卡流量监控


import psutil
from fastapi.logger import logger
import threading
import time

_network_stats = {
    'last_time': None,
    'last_upload': 0,        
    'last_download': 0,      
}
_history_lock = threading.Lock()

def get_system_traffic():
    """检测实时网络流量（上行/下行）"""
    logger.info("Starting network traffic detection")
    
    try:
        # 获取网络IO统计
        network_io = psutil.net_io_counters()
        current_time = time.time()
        
        upload_speed = 0
        download_speed = 0
        
        with _history_lock:
            if _network_stats['last_time'] is not None:
                time_diff = current_time - _network_stats['last_time']
                if time_diff >= 0.1:  
                    upload_diff = network_io.bytes_sent - _network_stats['last_upload']
                    download_diff = network_io.bytes_recv - _network_stats['last_download']
                    
                    upload_speed_mb = upload_diff / (time_diff * 1024 * 1024)
                    download_speed_mb = download_diff / (time_diff * 1024 * 1024)
                    upload_speed_kb = upload_diff / (time_diff * 1024)
                    download_speed_kb = download_diff / (time_diff * 1024)
                    
                    upload_speed = f"{upload_speed_mb:.6f} MB/s ({upload_speed_kb:.2f} KB/s)"
                    download_speed = f"{download_speed_mb:.6f} MB/s ({download_speed_kb:.2f} KB/s)"
            
            # 更新基准值
            _network_stats['last_time'] = current_time
            _network_stats['last_upload'] = network_io.bytes_sent
            _network_stats['last_download'] = network_io.bytes_recv

        current_time_formatted = time.strftime("%H:%M:%S", time.localtime())
        
        result = {
            "network": {
                "time": current_time_formatted,
                "realtime_speed": {
                    "upload": upload_speed or "0.00 MB/s",
                    "download": download_speed or "0.00 MB/s"
                }
            }
        }

        logger.info(f"[{current_time_formatted}] Network traffic detected: Upload {upload_speed or '0.00 MB/s'} | Download {download_speed or '0.00 MB/s'}")
        return result
    
    except Exception as e:
        logger.error(f"Error calculating network traffic: {str(e)}")
        return {"error": "network_monitoring_failed", "message": str(e)}