# 协议安全检测
# 检测内容：Windows防火墙启用检测、SYN攻击保护检测（基于注册表）、远程桌面端口修改检测（基于注册表）


import subprocess
import re
import winreg  # 用于注册表操作

def get_rules_protocols():
    # Windows防火墙启用检测
    def check_firewall_status():
        try:
            # 获取防火墙各配置文件状态（域、专用、公用）
            firewall_output = subprocess.getoutput('netsh advfirewall show allprofiles state')
            # 提取每个配置文件的启用状态（正则匹配"状态"后的内容，去掉冒号）
            statuses = re.findall(r"状态\s+([^\n]+)", firewall_output)  # 修改此处：移除冒号匹配
            
            # 统计已启用的配置文件数量
            enabled_count = sum(1 for status in statuses if "启用" in status)
            actual_status = f"{enabled_count}个已启用"
            
            return {
                "实际值": actual_status,
                "基线标准": "应启用所有网络配置文件的Windows防火墙（域、专用、公用，共3个）",
                "是否符合": "符合" if enabled_count == 3 else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # SYN攻击保护检测（基于注册表）
    def check_syn_attack_protection():
        try:
            # 打开TCP/IP参数注册表项
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters")
            # 获取SynAttackProtect值（类型为DWORD，默认不存在时返回0）
            syn_value, _ = winreg.QueryValueEx(key, "SynAttackProtect")
            
            return {
                "实际值": syn_value,
                "基线标准": "应启用SYN攻击保护（建议值：2）",
                "是否符合": "符合" if syn_value == 2 else "不符合"
            }
        except FileNotFoundError:
            return {"实际值": "未配置", "基线标准": "应启用SYN攻击保护（建议值：2）", "是否符合": "不符合"}
        except Exception as e:
            return {"error": str(e)}

    # 远程桌面端口修改检测（基于注册表）
    def check_rdp_port():
        try:
            # 打开远程桌面配置注册表项
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp")
            # 获取端口号（类型为DWORD，默认3389）
            port, _ = winreg.QueryValueEx(key, "PortNumber")
            
            return {
                "实际值": port,
                "基线标准": "应修改远程桌面默认端口（非3389）",
                "是否符合": "符合" if port != 3389 else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合安全策略检测
    def check_security_policy():
        try:
            return {
                "firewall_status": check_firewall_status(),
                "syn_attack_protection": check_syn_attack_protection(),
                "rdp_port": check_rdp_port()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "security_policy": check_security_policy()
    }
    
    return config_data