# 动态网络配置检测
# 检测内容：防火墙规则、DNS服务器验证、远程桌面端口、路由表与默认网关、IPv6安全设置

import subprocess
import winreg
import re

def check_firewall_rules():
    """检测防火墙规则"""
    try:
        result = subprocess.run(
            ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        return {
            "name": "防火墙规则",
            "status": "正常" if "启用" in result.stdout else "异常",
            "detail": result.stdout
        }
    except Exception as e:
        return {"name": "防火墙规则", "status": "检测失败", "detail": str(e)}

def check_dns_servers():
    """验证DNS服务器配置"""
    try:
        result = subprocess.run(
            ['ipconfig', '/all'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        dns_servers = re.findall(r'DNS 服务器[^\d]+(\d+\.\d+\.\d+\.\d+)', result.stdout)
        return {
            "name": "DNS服务器",
            "status": "正常" if dns_servers else "异常",
            "detail": f"当前DNS服务器: {', '.join(dns_servers) if dns_servers else '未找到'}",
            "recommendation": "建议使用可靠的DNS服务器（如 8.8.8.8 或 114.114.114.114）"
        }
    except Exception as e:
        return {"name": "DNS服务器", "status": "检测失败", "detail": str(e)}

def check_remote_desktop_port():
    """检测远程桌面端口设置"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           r"SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp")
        port, _ = winreg.QueryValueEx(key, "PortNumber")
        return {
            "name": "远程桌面端口",
            "status": "高风险" if port == 3389 else "正常",
            "detail": f"当前端口号: {port}",
            "recommendation": "建议修改默认3389端口" if port == 3389 else ""
        }
    except Exception as e:
        return {"name": "远程桌面端口", "status": "检测失败", "detail": str(e)}

def check_routing_table():
    """检测路由表和默认网关"""
    try:
        result = subprocess.run(
            ['route', 'print'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        has_default_gateway = "0.0.0.0" in result.stdout
        return {
            "name": "路由表与网关",
            "status": "正常" if has_default_gateway else "异常",
            "detail": "存在默认网关" if has_default_gateway else "未找到默认网关"
        }
    except Exception as e:
        return {"name": "路由表与网关", "status": "检测失败", "detail": str(e)}

def check_ipv6_security():
    """检测IPv6安全设置"""
    try:
        result = subprocess.run(
            ['netsh', 'interface', 'ipv6', 'show', 'global'],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        return {
            "name": "IPv6安全设置",
            "status": "正常" if "随机化标识" in result.stdout else "警告",
            "detail": result.stdout
        }
    except Exception as e:
        return {"name": "IPv6安全设置", "status": "检测失败", "detail": str(e)}

def get_detect_telnet():
    """主检测函数"""
    return [
        check_firewall_rules(),
        check_dns_servers(),
        check_remote_desktop_port(),
        check_routing_table(),
        check_ipv6_security()
    ]


