# 其他规则检测
# 检测内容：登录超时（≤600 秒）、设置 SSH 登录 Banner（前后）

import platform
import subprocess
import re
import os

def get_rules_other():
    # 获取基础信息
    hostname = platform.node()
    domain = subprocess.getoutput("dnsdomainname").strip() or "N/A"

    # 登录超时检测（≤600秒）
    def check_login_timeout():
        try:
            ssh_config = subprocess.getoutput("cat /etc/ssh/sshd_config 2>/dev/null")
            # 提取 ClientAliveInterval（服务器向客户端发送消息的时间间隔）和 ClientAliveCountMax（无响应次数）
            interval_match = re.search(r"^ClientAliveInterval\s+(\d+)", ssh_config, re.MULTILINE)
            count_match = re.search(r"^ClientAliveCountMax\s+(\d+)", ssh_config, re.MULTILINE)
            
            interval = int(interval_match.group(1)) if interval_match else 0
            count = int(count_match.group(1)) if count_match else 0
            total_timeout = interval * count if interval > 0 and count > 0 else "未配置"

            return {
                "实际值": {
                    "ClientAliveInterval": interval_match.group(1) if interval_match else "未配置",
                    "ClientAliveCountMax": count_match.group(1) if count_match else "未配置",
                    "总超时(秒)": total_timeout if isinstance(total_timeout, int) else "未配置"
                },
                "基线标准": "登录超时应≤600秒（ClientAliveInterval × ClientAliveCountMax ≤ 600）",
                "是否符合": "符合" if (isinstance(total_timeout, int) and total_timeout <= 600) else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # SSH 登录 Banner 检测（前后）
    def check_ssh_banner():
        try:
            ssh_config = subprocess.getoutput("cat /etc/ssh/sshd_config 2>/dev/null")
            # 提取 Banner 配置路径（登录前提示）
            banner_match = re.search(r"^Banner\s+(/[\w/.]+)", ssh_config, re.MULTILINE)
            banner_path = banner_match.group(1) if banner_match else ""
            banner_exists = os.path.exists(banner_path) if banner_path else False

            return {
                "实际值": {
                    "Banner配置路径": banner_match.group(0) if banner_match else "未配置",
                    "Banner文件存在性": "存在" if banner_exists else "不存在"
                },
                "基线标准": "应配置 SSH 登录前 Banner（Banner 参数指向有效文件，如 /etc/issue.net）",
                "是否符合": "符合" if (banner_match and banner_exists) else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合安全策略检测
    def check_security_policy():
        try:
            return {
                "login_timeout": check_login_timeout(),
                "ssh_banner": check_ssh_banner()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data