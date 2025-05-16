# 协议安全相关检测
# 检测内容：禁用 Telnet，强制 SSH 加密协议、修改 SNMP 默认团体字（public/private）等

import platform
import subprocess
import re
import os

def get_rules_permissions():
    # 获取基础信息
    hostname = platform.node()
    domain = subprocess.getoutput("dnsdomainname").strip() or "N/A"

    # 禁用 Telnet 检测
    def check_telnet_disabled():
        try:
            # 检测 Telnet 服务状态（是否运行）
            telnet_status = subprocess.getoutput("systemctl is-active telnet 2>/dev/null")
            # 检测 Telnet 是否安装（Debian/Ubuntu 用 dpkg，RHEL/CentOS 用 rpm）
            telnet_installed = "telnetd" in subprocess.getoutput("dpkg -l | grep telnet 2>/dev/null") or \
                            "telnet-server" in subprocess.getoutput("rpm -qa | grep telnet 2>/dev/null")
            return {
                "实际值": {
                    "服务状态": telnet_status if telnet_status else "未安装",
                    "是否安装": "已安装" if telnet_installed else "未安装"
                },
                "基线标准": "应卸载 Telnet 服务（未安装且未运行）",
                "是否符合": "符合" if not telnet_installed and telnet_status != "active" else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 强制 SSH 加密协议检测（要求使用 SSHv2 及强加密算法）
    def check_ssh_encryption():
        try:
            ssh_config = subprocess.getoutput("cat /etc/ssh/sshd_config 2>/dev/null")
            # 检测协议版本（应设置为 Protocol 2）
            protocol = re.search(r"^Protocol\s+(\d+)", ssh_config, re.MULTILINE)
            # 检测是否禁用弱加密算法（示例检测 Ciphers）
            ciphers = re.search(r"^Ciphers\s+(.+)", ssh_config, re.MULTILINE)
            return {
                "实际值": {
                    "协议版本": protocol.group(1) if protocol else "未配置",
                    "加密算法": ciphers.group(1) if ciphers else "未配置"
                },
                "基线标准": "SSH 应使用 Protocol 2，且 Ciphers 应包含强加密算法（如 aes256-ctr）",
                "是否符合": "符合" if (protocol and protocol.group(1) == "2" and 
                                    ciphers and "aes256-ctr" in ciphers.group(1)) else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 修改 SNMP 默认团体字检测（检查 public/private）
    def check_snmp_community():
        try:
            snmp_config = subprocess.getoutput("cat /etc/snmp/snmpd.conf 2>/dev/null")
            # 检测只读团体字（rocommunity）和读写团体字（rwcommunity）
            ro_community = re.findall(r"rocommunity\s+(\w+)", snmp_config)
            rw_community = re.findall(r"rwcommunity\s+(\w+)", snmp_config)
            return {
                "实际值": {
                    "只读团体字": ro_community if ro_community else "未配置",
                    "读写团体字": rw_community if rw_community else "未配置"
                },
                "基线标准": "SNMP 团体字应修改为非默认值（禁止使用 public/private）",
                "是否符合": "符合" if (not any("public" in c for c in ro_community) and 
                                    not any("private" in c for c in rw_community)) else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合安全策略检测
    def check_security_policy():
        try:
            return {
                "telnet_disabled": check_telnet_disabled(),
                "ssh_encryption": check_ssh_encryption(),
                "snmp_community": check_snmp_community()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data