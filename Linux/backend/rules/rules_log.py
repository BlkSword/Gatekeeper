# 日志审计检测
# 检测内容：记录安全事件（登录失败、su 操作）

import platform
import subprocess
import re
import os

def get_rules_log():
    # 获取基础信息
    hostname = platform.node()
    domain = subprocess.getoutput("dnsdomainname").strip() or "N/A"

    # 登录失败日志记录检测
    def check_login_failure_log():
        try:
            # 检测rsyslog配置（Debian系和RHEL系通用逻辑）
            rsyslog_conf = subprocess.getoutput("cat /etc/rsyslog.conf 2>/dev/null")
            # 匹配auth相关日志目标（Debian系auth.* -> /var/log/auth.log；RHEL系authpriv.* -> /var/log/secure）
            log_target = re.search(r"^(auth|authpriv)\.\*\s+(/var/log/(auth\.log|secure))", rsyslog_conf, re.MULTILINE)
            
            # 检测日志文件是否存在且可写
            log_file = log_target.group(2) if log_target else ""
            log_writable = os.access(log_file, os.W_OK) if log_file else False

            return {
                "实际值": {
                    "配置路径": log_target.group(0) if log_target else "未配置",
                    "日志文件可写性": "可写" if log_writable else "不可写"
                },
                "基线标准": "应配置记录登录失败事件到系统日志（如/var/log/auth.log或/var/log/secure），且日志文件可写",
                "是否符合": "符合" if (log_target and log_writable) else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # su操作日志记录检测
    def check_su_operation_log():
        try:
            # 检测su操作是否被记录（通过pam模块或rsyslog）
            pam_su_conf = subprocess.getoutput("cat /etc/pam.d/su 2>/dev/null")
            rsyslog_conf = subprocess.getoutput("cat /etc/rsyslog.conf 2>/dev/null")
            
            # 检查pam是否记录su事件（pam_tty_audit或pam_audit）
            pam_audit = re.search(r"pam_(tty_audit|audit)\.so", pam_su_conf)
            # 检查rsyslog是否单独记录su事件（可选）
            rsyslog_su = re.search(r"local[0-9]\.\*\s+/var/log/su\.log", rsyslog_conf, re.MULTILINE)

            return {
                "实际值": {
                    "pam审计配置": "已配置" if pam_audit else "未配置",
                    "独立su日志": "已配置" if rsyslog_su else "未配置"
                },
                "基线标准": "应通过PAM模块记录su操作的成功/失败事件（如启用pam_audit），建议配置独立su日志文件",
                "是否符合": "符合" if pam_audit else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合安全策略检测
    def check_security_policy():
        try:
            return {
                "login_failure_log": check_login_failure_log(),
                "su_operation_log": check_su_operation_log()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data