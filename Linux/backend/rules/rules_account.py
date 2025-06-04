# 账号规则相关检测
# 检测内容：限制 root 用户远程登录（SSH/Telnet）、检测无关账号（如 adm、lp、ftp 等）、
# 密码复杂度（至少 8 位，含大小写、数字、特殊字符）、密码生存期（≤90 天）、禁止空口令账号

import platform
import subprocess
import re
import os

def get_rules_account():
    # 获取基础信息
    hostname = platform.node()
    domain = subprocess.getoutput("dnsdomainname").strip() or "N/A"

    # 账户策略解析（密码复杂度、生存期等）
    def parse_account_policy():
        # 密码复杂度检测（基于/etc/security/pwquality.conf）
        pwquality = subprocess.getoutput("cat /etc/security/pwquality.conf 2>/dev/null")
        # 密码生存期检测（基于chage命令）
        root_age = subprocess.getoutput("chage -l root 2>/dev/null")
        return {
            "密码复杂度": {
                "最小长度": re.search(r"minlen\s*=\s*(\d+)", pwquality).group(1) if re.search(r"minlen", pwquality) else "未配置",
                "最少字符类型": re.search(r"minclass\s*=\s*(\d+)", pwquality).group(1) if re.search(r"minclass", pwquality) else "未配置"
            },
            "密码生存期(天)": re.search(r"MaxDays\s*=\s*(\d+)", root_age).group(1) if re.search(r"MaxDays", root_age) else "未配置"
        }

    # 无关账号检测（如adm、lp、ftp等）
    def check_unrelated_accounts():
        try:
            # 获取系统用户列表
            users = subprocess.getoutput("getent passwd | awk -F: '{print $1}'").split()
            # 定义需要检测的无关账号列表
            target_accounts = ["adm", "lp", "ftp"]
            existing_accounts = [acc for acc in target_accounts if acc in users]
            return {
                "实际值": existing_accounts,
                "基线标准": "应删除或禁用无关系统账号（如adm、lp、ftp）",
                "是否符合": "符合" if not existing_accounts else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # root远程登录检测（SSH/Telnet）
    def check_root_remote_login():
        try:
            # 检测SSH配置
            ssh_config = subprocess.getoutput("cat /etc/ssh/sshd_config 2>/dev/null")
            permit_root_ssh = re.search(r"^PermitRootLogin\s+(\w+)", ssh_config, re.MULTILINE)
            # 检测Telnet服务（默认不安装，若存在则检查）
            telnet_installed = "telnet" in subprocess.getoutput("dpkg -l | grep telnet")  # Debian系示例
            return {
                "SSH配置": permit_root_ssh.group(1) if permit_root_ssh else "未配置",
                "Telnet服务": "已安装" if telnet_installed else "未安装",
                "基线标准": "SSH应禁止root直接登录（PermitRootLogin no），应卸载Telnet服务",
                "是否符合": "符合" if (permit_root_ssh and permit_root_ssh.group(1) == "no") and not telnet_installed else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 禁止空口令账号检测
    def check_empty_password():
        try:
            shadow_content = subprocess.getoutput("sudo cat /etc/shadow 2>/dev/null")
            empty_users = [line.split(":")[0] for line in shadow_content.splitlines() if line.split(":")[1] in ["!", "*", ""]]
            return {
                "实际值": empty_users,
                "基线标准": "禁止存在空口令账号",
                "是否符合": "符合" if not empty_users else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合安全策略检测
    def check_security_policy():
        try:
            account_policy = parse_account_policy()
            return {
                "account_policy": {
                    "密码复杂度": {
                        "实际值": {
                            "最小长度": account_policy["密码复杂度"]["最小长度"],
                            "最少字符类型": account_policy["密码复杂度"]["最少字符类型"]
                        },
                        "基线标准": {
                            "最小长度": "建议至少8位",
                            "最少字符类型": "建议至少4种（大小写、数字、特殊字符）"
                        },
                        "是否符合": {
                            "最小长度": "符合" if (account_policy["密码复杂度"]["最小长度"] != "未配置" 
                                                and int(account_policy["密码复杂度"]["最小长度"]) >= 8) else "不符合",
                            "最少字符类型": "符合" if (account_policy["密码复杂度"]["最少字符类型"] != "未配置" 
                                                and int(account_policy["密码复杂度"]["最少字符类型"]) >= 4) else "不符合"
                        }
                    },
                    "密码生存期(天)": {
                        "实际值": account_policy["密码生存期(天)"],
                        "基线标准": "建议不超过90天",
                        "是否符合": "符合" if (account_policy["密码生存期(天)"] != "未配置" 
                                            and int(account_policy["密码生存期(天)"]) <= 90) else "不符合"
                    }
                },
                "unrelated_accounts": check_unrelated_accounts(),
                "root_remote_login": check_root_remote_login(),
                "empty_password": check_empty_password()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data