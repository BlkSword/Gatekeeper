# 内核相关检测
# 检测内容：禁止 ICMP 重定向 / 源路由、关闭数据包转发（非路由系统）、内核版本为最新

import platform
import subprocess
import re
import os

def get_rules_kernel():
    # 获取基础信息
    hostname = platform.node()
    domain = subprocess.getoutput("dnsdomainname").strip() or "N/A"

    # 禁止 ICMP 重定向/源路由检测
    def check_icmp_redirect_source_route():
        try:
            # 获取 ICMP 重定向和源路由配置（sysctl 参数）
            sysctl_output = subprocess.getoutput("sysctl net.ipv4.conf.all.accept_redirects net.ipv4.conf.all.accept_source_route 2>/dev/null")
            accept_redirects = re.search(r"net\.ipv4\.conf\.all\.accept_redirects\s*=\s*(\d+)", sysctl_output)
            accept_source_route = re.search(r"net\.ipv4\.conf\.all\.accept_source_route\s*=\s*(\d+)", sysctl_output)
            
            return {
                "实际值": {
                    "ICMP重定向": accept_redirects.group(1) if accept_redirects else "未配置",
                    "源路由": accept_source_route.group(1) if accept_source_route else "未配置"
                },
                "基线标准": "应禁止 ICMP 重定向和源路由（net.ipv4.conf.all.accept_redirects=0，net.ipv4.conf.all.accept_source_route=0）",
                "是否符合": "符合" if (accept_redirects and accept_redirects.group(1) == "0" 
                                    and accept_source_route and accept_source_route.group(1) == "0") else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 关闭数据包转发（非路由系统）检测
    def check_ip_forward():
        try:
            # 获取数据包转发配置（sysctl 参数）
            ip_forward = subprocess.getoutput("sysctl net.ipv4.ip_forward 2>/dev/null")
            forward_value = re.search(r"net\.ipv4\.ip_forward\s*=\s*(\d+)", ip_forward)
            
            return {
                "实际值": forward_value.group(1) if forward_value else "未配置",
                "基线标准": "非路由系统应关闭数据包转发（net.ipv4.ip_forward=0）",
                "是否符合": "符合" if (forward_value and forward_value.group(1) == "0") else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 内核版本为最新检测
    def check_kernel_version():
        try:
            # 获取当前内核版本
            current_version = subprocess.getoutput("uname -r").strip()
            # 获取最新内核版本（示例：通过包管理器查询，这里简化为提示用户确认）
            # 实际场景可根据系统类型使用 apt list --upgradable 或 yum check-update 等命令
            latest_version = "假设通过包管理器获取的最新版本"  # 需根据实际环境调整
            
            return {
                "实际值": current_version,
                "基线标准": f"应使用最新内核版本（当前最新：{latest_version}）",
                "是否符合": "符合" if current_version == latest_version else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合安全策略检测
    def check_security_policy():
        try:
            return {
                "icmp_redirect_source_route": check_icmp_redirect_source_route(),
                "ip_forward": check_ip_forward(),
                "kernel_version": check_kernel_version()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data