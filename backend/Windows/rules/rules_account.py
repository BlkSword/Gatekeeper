# 账号规则相关检测
# 检测内容：密码长度最小值，帐户锁定阈值，管理员账号重命名

import subprocess
import re
import os  

def get_rules_account():
    # 账户策略检测
    def parse_account_policy(policy):
        return {
            "密码最长使用期(天)": re.search(r"Maximum password age\s+(\d+)", policy).group(1) if re.search(r"Maximum password age\s+(\d+)", policy) else "未配置",
            "密码最短使用期(天)": re.search(r"Minimum password age\s+(\d+)", policy).group(1) if re.search(r"Minimum password age\s+(\d+)", policy) else "未配置",
            "密码历史记录": re.search(r"Length of password history maintained\s+(\d+)", policy).group(1) if re.search(r"Length of password history", policy) else "未配置",
            "密码长度最小值": re.search(r"Minimum password length\s+(\d+)", policy).group(1) if re.search(r"Minimum password length", policy) else "未配置"
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
                "默认管理员重命名": "已重命名" if not default_admin_exists else "未重命名",
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
            
            # 解析策略
            policy_data = parse_account_policy(account_policy)
            items = []
            counter = 1
            
            # 密码最长使用期
            max_age = policy_data["密码最长使用期(天)"]
            items.append({
                "序号": counter,
                "检测名称": "密码最长使用期(天)",
                "检测结果": max_age,
                "基线标准": "建议不超过90天",
                "是否符合": "符合" if max_age != "未配置" and int(max_age) <= 90 else "不符合"
            })
            counter += 1
            
            # 密码最短使用期
            min_age = policy_data["密码最短使用期(天)"]
            items.append({
                "序号": counter,
                "检测名称": "密码最短使用期(天)",
                "检测结果": min_age,
                "基线标准": "建议至少1天",
                "是否符合": "符合" if min_age != "未配置" and int(min_age) >= 1 else "不符合"
            })
            counter += 1
            
            # 密码历史记录
            history = policy_data["密码历史记录"]
            items.append({
                "序号": counter,
                "检测名称": "密码历史记录",
                "检测结果": history,
                "基线标准": "建议至少保留24个历史密码",
                "是否符合": "符合" if history != "未配置" and int(history) >= 24 else "不符合"
            })
            counter += 1
            
            # 密码长度最小值
            length = policy_data["密码长度最小值"]
            items.append({
                "序号": counter,
                "检测名称": "密码长度最小值",
                "检测结果": length,
                "基线标准": "建议至少8位",
                "是否符合": "符合" if length != "未配置" and int(length) >= 8 else "不符合"
            })
            counter += 1
            
            # 密码复杂性策略
            items.append({
                "序号": counter,
                "检测名称": "密码复杂性策略",
                "检测结果": "已启用" if "1" in password_complexity else "未启用",
                "基线标准": "建议启用密码复杂性策略",
                "是否符合": "符合" if "1" in password_complexity else "不符合"
            })
            counter += 1
            
            # 管理员账号重命名
            admin_data = get_admin_users()
            items.append({
                "序号": counter,
                "检测名称": "默认管理员账号重命名",
                "检测结果": admin_data["默认管理员重命名"],
                "基线标准": admin_data["基线标准"],
                "是否符合": "符合" if admin_data["默认管理员重命名"] == "已重命名" else "不符合"
            })
            counter += 1
            
            # 账户锁定阈值
            items.append({
                "序号": counter,
                "检测名称": "账户锁定阈值",
                "检测结果": lockout_threshold,
                "基线标准": "建议3次失败登录后锁定",
                "是否符合": "符合" if lockout_threshold != "未配置" and int(lockout_threshold) <= 3 else "不符合"
            })
            
            return {
                "检测项": items
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "security_policy": check_security_policy()
    }
    
    return config_data