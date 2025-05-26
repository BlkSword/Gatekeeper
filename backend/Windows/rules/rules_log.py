# 日志规则相关检测
# 检测内容包含：审计策略、日志状态、日志大小及覆盖策略检测

import subprocess
import re

def get_rules_log():
    def check_account_login():
        try:
            audit_policy = subprocess.getoutput('auditpol /get /category:*')
            result = "成功,失败" if re.search(r"Logon\s+Success\s+Failure", audit_policy) else "未配置"
            return {
                "序号": 10,
                "检测名称": "账户登录事件检测",
                "检测结果": result,
                "基线标准": "应同时审计成功和失败",
                "是否符合": "符合" if result == "成功,失败" else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    def check_account_management():
        try:
            audit_policy = subprocess.getoutput('auditpol /get /category:*')
            result = "成功,失败" if re.search(r"User Account Management\s+Success\s+Failure", audit_policy) else "未配置"
            return {
                "序号": 11,
                "检测名称": "账户管理检测",
                "检测结果": result,
                "基线标准": "应同时审计成功和失败",
                "是否符合": "符合" if result == "成功,失败" else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    def check_object_access():
        try:
            audit_policy = subprocess.getoutput('auditpol /get /category:*')
            result = "成功" if re.search(r"Object Access\s+Success\s+.*Failure?", audit_policy) else "未配置"
            return {
                "序号": 12,
                "检测名称": "对象访问检测",
                "检测结果": result,
                "基线标准": "应审计成功",
                "是否符合": "符合" if result == "成功" else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 日志状态检测（序号13）
    def check_log_status():
        try:
            system_log = subprocess.getoutput('wevtutil get-log System')
            security_log = subprocess.getoutput('wevtutil get-log Security')
            system_status = "已启用" if "enabled: true" in system_log else "未启用"
            security_status = "已启用" if "enabled: true" in security_log else "未启用"
            compliant = system_status == "已启用" and security_status == "已启用"
            return {
                "序号": 13,
                "检测名称": "日志状态检测",
                "检测结果": {
                    "系统日志": system_status,
                    "安全日志": security_status
                },
                "基线标准": "系统日志和安全日志都应启用",
                "是否符合": "符合" if compliant else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 安全日志大小检测（序号14）
    def check_security_log_size():
        try:
            security_log_xml = subprocess.getoutput('wevtutil gl Security /f:xml')
            max_size_match = re.search(r'<MaxSize>(\d+)</MaxSize>', security_log_xml)
            if max_size_match:
                max_size_mb = int(max_size_match.group(1)) // (1024*1024)
                result = f"{max_size_mb}MB"
            else:
                result = "未配置"
            compliant = "符合" if (isinstance(max_size_match, re.Match) and max_size_mb >= 2048) else "不符合"
            return {
                "序号": 14,
                "检测名称": "安全日志大小检测",
                "检测结果": result,
                "基线标准": "应设置为不小于2048MB",
                "是否符合": compliant
            }
        except Exception as e:
            return {"error": str(e)}

    # 日志覆盖策略检测（序号15）
    def check_log_retention():
        try:
            security_log_xml = subprocess.getoutput('wevtutil gl Security /f:xml')
            retention_match = re.search(r'<Retention>(\d)</Retention>', security_log_xml)
            if retention_match:
                policy = "覆盖旧日志" if retention_match.group(1) == "0" else "不覆盖旧日志"
            else:
                policy = "未配置"
            compliant = "符合" if policy == "不覆盖旧日志" else "不符合"
            return {
                "序号": 15,
                "检测名称": "安全日志覆盖策略检测",
                "检测结果": policy,
                "基线标准": "应配置为不覆盖旧日志（保留历史记录）",
                "是否符合": compliant
            }
        except Exception as e:
            return {"error": str(e)}

    # 执行所有检测并整合结果
    return {
        "security_policy": {
            "account_login": check_account_login(),
            "account_management": check_account_management(),
            "object_access": check_object_access(),
            "log_status": check_log_status(),
            "security_log_size": check_security_log_size(),
            "log_retention": check_log_retention()
        }
    }