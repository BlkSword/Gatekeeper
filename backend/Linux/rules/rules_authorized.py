# 认证授权检测
# 检测内容：最小权限原则（用户 / 文件权限）、禁止 wheel 组外用户 su 至 root

import platform
import subprocess
import re
import os

def get_rules_authorized():
    # 获取基础信息
    hostname = platform.node()
    domain = subprocess.getoutput("dnsdomainname").strip() or "N/A"

    # 最小权限原则检测（用户/文件权限）
    def check_minimum_privilege():
        try:
            # 用户权限检测：非特权用户（UID>=1000）是否存在不必要的高权限
            users = subprocess.getoutput("getent passwd | awk -F: '{print $1,$3}'").splitlines()
            privileged_users = [user.split()[0] for user in users if int(user.split()[1]) < 1000 and user.split()[0] not in ["root"]]
            
            # 文件权限检测：关键文件（如/etc/shadow）权限是否为600（仅root可读）
            shadow_perm = subprocess.getoutput("stat -c %a /etc/shadow 2>/dev/null") or "未配置"
            
            return {
                "实际值": {
                    "特权用户": privileged_users,
                    "关键文件权限(/etc/shadow)": shadow_perm
                },
                "基线标准": {
                    "特权用户": "仅允许必要的系统用户（如root）拥有特权UID（<1000）",
                    "关键文件权限": "关键文件（如/etc/shadow）权限应设置为600"
                },
                "是否符合": {
                    "特权用户": "符合" if not privileged_users else "不符合",
                    "关键文件权限": "符合" if shadow_perm == "600" else "不符合"
                }
            }
        except Exception as e:
            return {"error": str(e)}

    # 禁止wheel组外用户su至root检测
    def check_wheel_group_su():
        try:
            # 检查/etc/pam.d/su配置是否启用wheel组限制
            su_config = subprocess.getoutput("cat /etc/pam.d/su 2>/dev/null")
            wheel_enabled = re.search(r"^auth\s+required\s+pam_wheel\.so\s+use_uid", su_config, re.MULTILINE) is not None
            
            return {
                "实际值": "已启用" if wheel_enabled else "未启用",
                "基线标准": "应启用wheel组限制（/etc/pam.d/su中包含'auth required pam_wheel.so use_uid'）",
                "是否符合": "符合" if wheel_enabled else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合安全策略检测
    def check_security_policy():
        try:
            return {
                "minimum_privilege": check_minimum_privilege(),
                "wheel_group_su": check_wheel_group_su()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data