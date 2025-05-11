# 获取主机网络信息
# 检测内容有：网络接口信息、数据统计、开放端口、防火墙规则、网络服务配置

import socket
import psutil
import subprocess
import logging

logger = logging.getLogger(__name__)

def get_network_status():
    """获取网络状态信息"""
    
    # 获取网关信息（Linux适配）
    def get_gateways():
        try:
            # Linux使用ip命令获取默认网关
            result = subprocess.check_output(
                'ip route show default', 
                shell=True, 
                encoding='utf-8',
                stderr=subprocess.STDOUT
            )
            gateways = []
            for line in result.split('\n'):
                if 'default via' in line:
                    # 示例行格式: "default via 192.168.1.1 dev eth0 proto static"
                    parts = line.split()
                    gateways.append(parts[2])  # 提取网关IP
            return list(set(gateways))
        except Exception as e:
            return {"error": str(e)}

    # 获取开放端口（跨平台，无需修改）
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

    # 获取防火墙规则（Linux适配）
    def get_firewall_rules():
        try:
            # Linux使用iptables获取规则（需root权限）
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
                # 处理链名称（如INPUT、FORWARD）
                if line.startswith('Chain '):
                    current_chain = line.split()[1]
                # 跳过表头行（如"num  target     prot opt source               destination"）
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

    # 获取网络服务配置（跨平台，无需大修改）
    def get_network_services():
        try:
            services = []
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                if proc.info['connections']:
                    connections = proc.connections()
                    services.append({
                        "name": proc.info['name'],
                        "pid": proc.info['pid'],
                        "exe_path": proc.exe(),  # Linux下返回进程可执行文件路径
                        "protocols": list({conn.type.name for conn in connections if conn.type})
                    })
            return services
        except Exception as e:
            return {"error": str(e)}

    return {
        "network_interfaces": {
            name: {
                "ip_address": [addr.address for addr in addrs if addr.family == socket.AF_INET],
                "netmask": [addr.netmask for addr in addrs if addr.family == socket.AF_INET],
                "gateways": get_gateways()  # 网关信息（Linux适配）
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
        "dns_servers": [
            # Linux下通过读取/etc/resolv.conf获取DNS更可靠，此处保留原逻辑但需注意兼容性
            dns[-1][0] for dns in socket.getaddrinfo(
                socket.gethostname(), 
                None, 
                proto=socket.IPPROTO_UDP,
                type=socket.SOCK_DGRAM
            )
        ]
    }