# 账号规则相关检测
# 检测内容：密码长度最小值，帐户锁定阈值，管理员账号重命名

import platform
import subprocess
import re
import socket
import os  

def get_rules_account():
    # 获取基础信息
    hostname = platform.node()
    domain = socket.getfqdn().split('.', 1)[1] if '.' in socket.getfqdn() else "N/A"

    # 账户策略检测
    def parse_account_policy(policy):
        return {
            "密码最长使用期(天)": "未配置" if re.search(r"Maximum password age\s+None", policy) 
                          else re.search(r"Maximum password age\s+(\d+)", policy).group(1) if re.search(r"Maximum password age", policy) else "未配置",
            "密码最短使用期(天)": "未配置" if re.search(r"Minimum password age\s+None", policy) 
                          else re.search(r"Minimum password age\s+(\d+)", policy).group(1) if re.search(r"Minimum password age", policy) else "未配置",
            "密码历史记录": "未配置" if re.search(r"Length of password history maintained\s+None", policy) 
                     else re.search(r"Length of password history maintained\s+(\d+)", policy).group(1) if re.search(r"Length of password history", policy) else "未配置",
            "密码长度最小值": "未配置" if re.search(r"Minimum password length\s+0", policy)  
                          else re.search(r"Minimum password length\s+(\d+)", policy).group(1) if re.search(r"Minimum password length", policy) else "未配置"
        }
    
    # 管理员用户检测
    def get_admin_users():
        try:
            output = subprocess.getoutput('net localgroup administrators')
            # 过滤掉分隔线、空行和命令提示行
            admin_list = [line.strip() for line in output.split('\n') 
                    if line.strip() and not any(line.startswith(key) for key in ('--', '命令', '成员', 'The command completed successfully'))]
            
            # 检测默认管理员是否存在
            user_output = subprocess.getoutput('net user')
            default_admin_exists = "Administrator" in user_output
            return {
                "管理员列表": admin_list,
                "默认管理员重命名": "未重命名" if default_admin_exists else "已重命名",
                "基线标准": "应重命名默认管理员账号（Administrator）"
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合安全策略检测
    def check_security_policy():
        try:
            account_policy = subprocess.getoutput('net accounts')
            temp_path = os.path.join(os.environ['TEMP'], 'secpol.cfg')
            password_complexity = subprocess.getoutput(f'secedit /export /cfg {temp_path} && find "PasswordComplexity" {temp_path}')
            
            # 获取账户锁定阈值
            lockout_output = subprocess.getoutput(f'find "LockoutThreshold" {temp_path}')
            lockout_threshold = re.search(r"LockoutThreshold\s+=\s+(\d+)", lockout_output).group(1) if re.search(r"LockoutThreshold\s+=\s+(\d+)", lockout_output) else "未配置"
            
            return {
                "account_policy": {
                    **parse_account_policy(account_policy),
                    "基线标准": {
                        "密码最长使用期(天)": "建议不超过90天",
                        "密码最短使用期(天)": "建议至少1天",
                        "密码历史记录": "建议至少保留24个历史密码",
                        "密码长度最小值": "建议至少8位"
                    },
                    "是否符合": {
                        "密码最长使用期(天)": "符合" if parse_account_policy(account_policy)["密码最长使用期(天)"] != "未配置" and int(parse_account_policy(account_policy)["密码最长使用期(天)"]) <= 90 else "不符合",
                        "密码最短使用期(天)": "符合" if parse_account_policy(account_policy)["密码最短使用期(天)"] != "未配置" and int(parse_account_policy(account_policy)["密码最短使用期(天)"]) >= 1 else "不符合",
                        "密码历史记录": "符合" if parse_account_policy(account_policy)["密码历史记录"] != "未配置" and int(parse_account_policy(account_policy)["密码历史记录"]) >= 24 else "不符合",
                        "密码长度最小值": "符合" if parse_account_policy(account_policy)["密码长度最小值"] != "未配置" and int(parse_account_policy(account_policy)["密码长度最小值"]) >= 8 else "不符合"
                    }
                },
                "password_complexity": "已启用" if "1" in password_complexity else "未启用",
                "admin_users": {
                    **get_admin_users(),
                    "是否符合": "符合" if get_admin_users()["默认管理员重命名"] == "已重命名" else "不符合"
                },
                "account_lockout": {  # 保留账户锁定检测项
                    "实际值": lockout_threshold,
                    "基线标准": "建议3次失败登录后锁定",
                    "是否符合": "符合" if lockout_threshold != "未配置" and int(lockout_threshold) <= 3 else "不符合"
                }
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data