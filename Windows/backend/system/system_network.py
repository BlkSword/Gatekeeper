# 获取主机网络信息
# 检测内容有：网络接口信息、数据统计、开放端口、防火墙规则、网络服务


import socket
import psutil
import subprocess
import logging

logger = logging.getLogger(__name__)

def get_network_status():
    """获取网络状态信息"""
    
    # 获取网关信息函数
    def get_gateways():
        try:
            result = subprocess.check_output('route print 0.0.0.0', shell=True, encoding='gbk')
            gateways = []
            for line in result.split('\n'):
                if '0.0.0.0' in line and '在链路上' not in line:
                    parts = line.split()
                    if len(parts) > 4:
                        gateways.append(parts[3])
            return list(set(gateways))
        except Exception as e:
            return {"error": str(e)}

    # 获取开放端口
    def get_open_ports():
        try:
            connections = psutil.net_connections(kind='inet')
            return [
                {
                    "protocol": conn.type.name,
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
                    "status": conn.status
                } 
                for conn in connections if conn.status == 'LISTEN'
            ]
        except Exception as e:
            return {"error": str(e)}

    # 获取防火墙规则
    def get_firewall_rules():
        try:
            result = subprocess.check_output(
                'netsh advfirewall firewall show rule name=all',
                shell=True,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='gbk'
            )
            
            rules = []
            current_rule = {}
            for line in result.split('\n'):
                line = line.strip()
                if line.startswith('规则名称'):
                    if current_rule:
                        rules.append(current_rule)
                    current_rule = {"name": line.split(':', 1)[1].strip()}
                elif line and ':' in line:
                    key, value = line.split(':', 1)
                    current_rule[key.strip()] = value.strip()
            if current_rule:
                rules.append(current_rule)
            return rules
        except Exception as e:
            logger.error(f"Failed to get firewall rules: {str(e)}")
            return {"error": str(e)}

    # 获取使用网络服务
    def get_network_services():
        try:
            services = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    connections = proc.connections()
                    if connections:
                        protocols = list({conn.type.name for conn in connections if conn.type})
                        services.append({
                            "name": proc.info['name'],
                            "pid": proc.info['pid'],
                            "exe_path": proc.info['exe'],
                            "protocols": protocols
                        })
                except psutil.AccessDenied:
                    continue  
            return services
        except Exception as e:
            return {"error": str(e)}

    return {
        "network_interfaces": {
            name: {
                "ip_address": [addr.address for addr in addrs if addr.family == socket.AF_INET],
                "netmask": [addr.netmask for addr in addrs if addr.family == socket.AF_INET],
                "gateways": get_gateways()  
            }
            for name, addrs in psutil.net_if_addrs().items()
        },
        "data_usage": {
            "sent_MB": psutil.net_io_counters().bytes_sent / (1024**2),
            "recv_MB": psutil.net_io_counters().bytes_recv / (1024**2)
        },
        "open_ports": get_open_ports(),
        "firewall_rules": get_firewall_rules(),
        "network_services": get_network_services(),
    }