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

    # 获取防火墙规则（仅解析 ufw-user-input 链）
    def get_firewall_rules():
        try:
            result = subprocess.run(
                'sudo iptables -L -n -v --line-numbers',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                encoding='utf-8'
            )

            if result.returncode != 0:
                logger.error(f"执行 iptables 命令失败: {result.stderr}")
                return {"error": result.stderr}

            output = result.stdout
            rules_section = False
            rules = []

            for line in output.split('\n'):
                line = line.strip()

                # 开始解析 ufw-user-input 链
                if line.startswith('Chain ufw-user-input'):
                    rules_section = True
                    continue

                # 结束解析其他链
                if rules_section and line.startswith('Chain '):
                    break

                # 解析规则行
                if rules_section and line and not line.startswith('num '):
                    parts = line.split()
                    if len(parts) >= 8:
                        try:
                            rule = {
                                "num": int(parts[0]),
                                "pkts": int(parts[1]),
                                "bytes": int(parts[2]),
                                "target": parts[3],
                                "prot": parts[4],
                                "source": parts[7].split(':')[0],  # 忽略端口部分
                                "destination": parts[8].split(':')[0]  # 忽略端口部分
                            }
                            rules.append(rule)
                        except (ValueError, IndexError) as e:
                            logger.warning(f"解析规则失败: {line} - {e}")
                            continue

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

# if __name__ == "__main__":
#     network_info = get_network_status()
#     print(network_info["firewall_rules"])