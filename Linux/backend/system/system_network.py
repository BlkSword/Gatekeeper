# 获取主机网络信息
# 检测内容有：网络接口信息、数据统计、开放端口、防火墙规则、网络服务

import socket
import psutil
import subprocess
import logging

logger = logging.getLogger(__name__)

def get_network_status():
    """获取网络状态信息"""
    
    # 获取网关信息
    def get_gateways():
        try:
            result = subprocess.check_output(
                'ip route show default', 
                shell=True, 
                encoding='utf-8',
                stderr=subprocess.STDOUT
            )
            gateways = []
            for line in result.split('\n'):
                if 'default via' in line:
                    parts = line.split()
                    gateways.append(parts[2])  
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
                'iptables -L -n -v --line-numbers',
                shell=True,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8'
            )
            
            rules = []
            current_chain = None
            for line in result.split('\n'):
                line = line.strip()
                if line.startswith('Chain '):
                    current_chain = line.split()[1]
                elif line and not line.startswith('num') and current_chain:
                    parts = line.split()
                    if len(parts) >= 7:
                        rules.append({
                            "chain": current_chain,
                            "num": parts[0],
                            "target": parts[1],
                            "prot": parts[2],
                            "opt": parts[3],
                            "source": parts[4],
                            "destination": parts[5]
                        })
            return rules
        except Exception as e:
            logger.error(f"获取防火墙规则失败: {str(e)}")
            return {"error": str(e)}

    # 网络服务获取函数
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