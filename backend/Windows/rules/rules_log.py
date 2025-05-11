# 日志规则相关检测
# 检测内容包含：审计策略、日志状态、日志大小及覆盖策略检测


import subprocess
import re

def get_rules_log():
    # 审计策略检测
    def parse_audit_policy(policy):
        return {
            "账户登录事件": "成功,失败" if re.search(r"Logon\s+Success\s+Failure", policy) else "未配置",
            "账户管理": "成功,失败" if re.search(r"User Account Management\s+Success\s+Failure", policy) else "未配置",
            "对象访问": "成功" if re.search(r"Object Access\s+Success\s+.*Failure?", policy) else "未配置"  # 允许失败项可选
        }

    # 整合审计策略检测
    def check_audit_policy():
        try:
            audit_policy = subprocess.getoutput('auditpol /get /category:*')
            parsed = parse_audit_policy(audit_policy)
            return {
                "审计策略": {
                    **parsed,
                    "基线标准": {
                        "账户登录事件": "应同时审计成功和失败",
                        "账户管理": "应同时审计成功和失败",
                        "对象访问": "应审计成功"
                    },
                    "是否符合": {
                        "账户登录事件": "符合" if parsed["账户登录事件"] == "成功,失败" else "不符合",
                        "账户管理": "符合" if parsed["账户管理"] == "成功,失败" else "不符合",
                        "对象访问": "符合" if parsed["对象访问"] == "成功" else "不符合"
                    }
                }
            }
        except Exception as e:
            return {"error": str(e)}

    # 日志综合检测（包含状态、大小、覆盖策略）
    def check_log_policy():
        try:
            # 获取日志状态
            system_log = subprocess.getoutput('wevtutil get-log System')
            security_log = subprocess.getoutput('wevtutil get-log Security')
            
            # 获取安全日志详细配置（XML格式便于解析）
            security_log_xml = subprocess.getoutput('wevtutil gl Security /f:xml')
            
            # 解析日志大小（单位：字节，转换为MB）
            max_size_match = re.search(r'<MaxSize>(\d+)</MaxSize>', security_log_xml)
            max_size_mb = int(max_size_match.group(1)) // (1024*1024) if max_size_match else "未配置"
            
            # 解析覆盖策略（0=覆盖，1=不覆盖）
            retention_match = re.search(r'<Retention>(\d)</Retention>', security_log_xml)
            retention_policy = "覆盖旧日志" if (retention_match and retention_match.group(1) == "0") else "不覆盖旧日志" if (retention_match and retention_match.group(1) == "1") else "未配置"

            return {
                "日志状态": {
                    "系统日志": "已启用" if "enabled: true" in system_log else "未启用",
                    "安全日志": "已启用" if "enabled: true" in security_log else "未启用"
                },
                "安全日志大小": {
                    "实际值": f"{max_size_mb}MB" if isinstance(max_size_mb, int) else "未配置",
                    "基线标准": "应设置为不小于2048MB",
                    "是否符合": "符合" if (isinstance(max_size_mb, int) and max_size_mb >= 2048) else "不符合"
                },
                "安全日志覆盖策略": {
                    "实际值": retention_policy,
                    "基线标准": "应配置为不覆盖旧日志（保留历史记录）",
                    "是否符合": "符合" if retention_policy == "不覆盖旧日志" else "不符合"
                }
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合所有检测结果
    return {
        "audit_policy": check_audit_policy(),
        "log_policy": check_log_policy()
    }