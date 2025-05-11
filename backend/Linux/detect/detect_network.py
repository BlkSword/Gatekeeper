# 网络配置监控
# 检测内容：防火墙状态、SELinux/AppArmor状态、内核网络参数、网络服务监听端口、路由表与默认网关
import subprocess
from typing import Dict, Any

def get_detect_network() -> Dict[str, Any]:
    """检测Linux系统网络配置，返回各检测项结果"""
    result = {}

    # 检测防火墙状态（支持firewalld和iptables）
    try:
        firewall_status = subprocess.check_output(
            "systemctl is-active firewalld 2>/dev/null || echo 'inactive'",
            shell=True, text=True
        ).strip()
        if firewall_status == "inactive":
            # 检查iptables是否运行
            iptables_status = subprocess.check_output(
                "systemctl is-active iptables 2>/dev/null || echo 'inactive'",
                shell=True, text=True
            ).strip()
            firewall_status = f"firewalld({firewall_status})/iptables({iptables_status})"
        result["firewall_status"] = firewall_status
    except Exception as e:
        result["firewall_status"] = f"检测失败: {str(e)}"

    # 检测SELinux/AppArmor状态
    try:
        selinux_info = subprocess.check_output("sestatus 2>/dev/null", shell=True, text=True).strip()
        result["selinux_status"] = "启用" if "enabled" in selinux_info else "禁用"
    except:
        result["selinux_status"] = "未检测到SELinux"

    try:
        apparmor_status = subprocess.check_output(
            "systemctl is-active apparmor 2>/dev/null || echo 'inactive'",
            shell=True, text=True
        ).strip()
        result["apparmor_status"] = apparmor_status
    except Exception as e:
        result["apparmor_status"] = f"检测失败: {str(e)}"

    # 检测内核网络参数（示例获取关键参数）
    try:
        kernel_params = subprocess.check_output(
            "sysctl net.ipv4.ip_forward net.ipv4.tcp_syncookies net.ipv6.conf.all.disable_ipv6",
            shell=True, text=True
        ).strip()
        result["kernel_network_params"] = dict(
            line.split(" = ") for line in kernel_params.split("\n") if " = " in line
        )
    except Exception as e:
        result["kernel_network_params"] = f"检测失败: {str(e)}"

    # 检测网络服务监听端口
    try:
        listening_ports = subprocess.check_output(
            "ss -tuln | awk 'NR>1 {print $1,$4}'", shell=True, text=True
        ).strip().split("\n")
        result["listening_ports"] = [line.strip() for line in listening_ports if line]
    except Exception as e:
        result["listening_ports"] = f"检测失败: {str(e)}"

    # 检测路由表与默认网关
    try:
        route_info = subprocess.check_output("ip route show", shell=True, text=True).strip()
        default_gateway = subprocess.check_output(
            "ip route show default | awk '{print $3}'", shell=True, text=True
        ).strip()
        result["route_table"] = route_info
        result["default_gateway"] = default_gateway if default_gateway else "无默认网关"
    except Exception as e:
        result["route_table"] = f"检测失败: {str(e)}"
        result["default_gateway"] = f"检测失败: {str(e)}"

    return result