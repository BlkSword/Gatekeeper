# 检测系统安全策略	
# 检测内容有：账户策略、密码复杂度、管理员用户、审计策略、安全设置、
# SELinux/AppArmor状态、sudoers配置、文件权限、内核安全参数、安全日志、安全审计


import platform
import subprocess
import re
import os
from datetime import datetime, timedelta

def get_system_config():
    # 获取基础信息
    hostname = platform.node()
    domain = subprocess.getoutput("dnsdomainname").strip() or "N/A"

    # 账户策略检测（基于chage命令和/etc/security/pwquality.conf）
    def parse_account_policy():
        # 获取全局密码策略（示例：最小长度、复杂度）
        pwquality = subprocess.getoutput("cat /etc/security/pwquality.conf 2>/dev/null")
        # 获取root用户密码有效期（需root权限）
        root_age = subprocess.getoutput("chage -l root 2>/dev/null")
        return {
            "密码最长使用期(天)": re.search(r"MaxDays\s*=\s*(\d+)", root_age).group(1) if re.search(r"MaxDays", root_age) else "未配置",
            "密码最短使用期(天)": re.search(r"MinDays\s*=\s*(\d+)", root_age).group(1) if re.search(r"MinDays", root_age) else "未配置",
            "密码历史记录": re.search(r"remember\s*=\s*(\d+)", pwquality).group(1) if re.search(r"remember", pwquality) else "未配置",
            "密码最小长度": re.search(r"minlen\s*=\s*(\d+)", pwquality).group(1) if re.search(r"minlen", pwquality) else "未配置"
        }
    
    # 审计策略检测（基于auditd）
    def parse_audit_policy():
        audit_rules = subprocess.getoutput("auditctl -l 2>/dev/null")
        return {
            "账户登录事件": "已配置" if re.search(r"-w /var/log/faillog", audit_rules) else "未配置",
            "账户管理": "已配置" if re.search(r"-w /etc/passwd", audit_rules) else "未配置",
            "对象访问": "已配置" if re.search(r"-w /etc/shadow", audit_rules) else "未配置"
        }
    
    # 管理员用户检测（UID=0或sudo组成员）
    def get_admin_users():
        try:
            # 获取UID=0的用户（通常为root）
            root_users = subprocess.getoutput("getent passwd | awk -F: '$3 == 0 {print $1}'").split()
            # 获取sudo组成员（Debian/Ubuntu）或wheel组（RHEL）
            sudo_group = "sudo" if os.path.exists("/etc/sudoers") else "wheel"
            sudo_users = subprocess.getoutput(f"getent group {sudo_group} | awk -F: '{{print $4}}'").split(',')
            return list(set(root_users + sudo_users))  # 去重
        except Exception as e:
            return {"error": str(e)}

    # 日志检测（检查rsyslog/syslog-ng状态）
    def check_log_settings():
        try:
            rsyslog_status = subprocess.getoutput("systemctl is-active rsyslog 2>/dev/null")
            journald_status = subprocess.getoutput("systemctl is-active systemd-journald 2>/dev/null")
            return {
                "system_log": "已启用" if rsyslog_status == "active" else "未启用",
                "security_log": "已启用" if journald_status == "active" else "未启用"
            }
        except Exception as e:
            return {"error": str(e)}

    # 安全事件检测（检查/var/log/secure或/var/log/auth.log）
    def check_security_events():
        try:
            log_path = "/var/log/secure" if os.path.exists("/var/log/secure") else "/var/log/auth.log"
            # 统计过去24小时的认证失败事件
            events = subprocess.getoutput(f"grep 'Failed password' {log_path} | awk -v date='{datetime.now()-timedelta(hours=24)}' '$0 > date' | wc -l")
            return {
                "security_events_count": int(events) if events.isdigit() else 0,
                "last_24h_events": int(events) > 0 if events.isdigit() else False
            }
        except Exception as e:
            return {"error": str(e)}

    # 安全审计检测（检查auditd服务状态）
    def check_security_audit():
        try:
            auditd_status = subprocess.getoutput("systemctl is-enabled auditd 2>/dev/null")
            return {
                "security_audit": "已启用" if auditd_status == "enabled" else "未启用"
            }
        except Exception as e:
            return {"error": str(e)}

    # SELinux/AppArmor状态检测
    def check_security_modules():
        selinux_status = subprocess.getoutput("sestatus 2>/dev/null | grep 'SELinux status' | awk '{print $3}'")
        apparmor_status = subprocess.getoutput("systemctl is-active apparmor 2>/dev/null")
        return {
            "selinux": "启用" if selinux_status == "enabled" else "禁用",
            "apparmor": "启用" if apparmor_status == "active" else "禁用"
        }

    # sudoers配置检测
    def check_sudoers():
        try:
            # 检查文件权限（应为0440）
            perms = subprocess.getoutput("stat -c %a /etc/sudoers 2>/dev/null")
            # 检查语法是否正确（visudo -c）
            syntax_check = subprocess.getoutput("visudo -c 2>/dev/null | grep 'syntax OK'")
            return {
                "权限配置": "正确（0440）" if perms == "440" else f"错误（当前：{perms}）",
                "语法状态": "正常" if "syntax OK" in syntax_check else "异常"
            }
        except Exception as e:
            return {"error": str(e)}

    # 文件权限检测（关键系统文件）
    def check_file_permissions():
        return {
            "/etc/passwd": subprocess.getoutput("stat -c %a /etc/passwd 2>/dev/null"),
            "/etc/shadow": subprocess.getoutput("stat -c %a /etc/shadow 2>/dev/null"),
            "/etc/sudoers": subprocess.getoutput("stat -c %a /etc/sudoers 2>/dev/null")
        }

    # 内核安全参数检测
    def check_kernel_params():
        return {
            "地址空间随机化": subprocess.getoutput("sysctl -n kernel.randomize_va_space 2>/dev/null"),
            "IP转发": subprocess.getoutput("sysctl -n net.ipv4.ip_forward 2>/dev/null"),
            "核心转储": subprocess.getoutput("sysctl -n fs.suid_dumpable 2>/dev/null")
        }

    # 整合安全策略检测
    def check_security_policy():
        try:
            return {
                "account_policy": parse_account_policy(),
                "password_complexity": "已启用" if re.search(r"minclass\s*=\s*[1-4]", subprocess.getoutput("cat /etc/security/pwquality.conf 2>/dev/null")) else "未启用",
                "admin_users": get_admin_users(),
                "audit_settings": parse_audit_policy(),
                "log_settings": check_log_settings(),
                "security_events": check_security_events(),
                "security_audit": check_security_audit(),
                "security_modules": check_security_modules(),
                "sudoers_config": check_sudoers(),
                "file_permissions": check_file_permissions(),
                "kernel_params": check_kernel_params()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data