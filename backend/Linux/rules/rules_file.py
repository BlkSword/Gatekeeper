# 文件相关检测
# 检测内容：禁止危险文件（.rhosts、hosts.equiv）、重要文件防篡改（/etc/passwd /etc/shadow /etc/group）

import platform
import subprocess
import re
import os

def get_rules_file():
    # 获取基础信息
    hostname = platform.node()
    domain = subprocess.getoutput("dnsdomainname").strip() or "N/A"

    # 禁止危险文件检测（.rhosts、hosts.equiv）
    def check_dangerous_files():
        try:
            # 检查系统中是否存在危险文件（常见路径：用户家目录、根目录）
            dangerous_files = [".rhosts", "hosts.equiv"]
            existing_files = []
            for file in dangerous_files:
                # 检查所有用户家目录（通过/etc/passwd获取家目录路径）
                home_dirs = subprocess.getoutput("getent passwd | awk -F: '{print $6}'").split()
                for home in home_dirs:
                    file_path = os.path.join(home, file)
                    if os.path.exists(file_path):
                        existing_files.append(file_path)
                # 检查根目录
                root_path = os.path.join("/", file)
                if os.path.exists(root_path):
                    existing_files.append(root_path)
            
            return {
                "实际值": existing_files,
                "基线标准": "应不存在危险文件（.rhosts、hosts.equiv）",
                "是否符合": "符合" if not existing_files else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 重要文件防篡改检测（/etc/passwd /etc/shadow /etc/group）
    def check_important_files_tamper():
        try:
            important_files = ["/etc/passwd", "/etc/shadow", "/etc/group"]
            check_results = {}
            
            for file in important_files:
                # 检测文件权限（示例：/etc/shadow应600，/etc/passwd和group应644）
                perm = subprocess.getoutput(f"stat -c %a {file} 2>/dev/null") or "未配置"
                # 检测是否设置不可变属性（lsattr返回包含i表示不可变）
                immutable = "是" if "i" in subprocess.getoutput(f"lsattr {file} 2>/dev/null") else "否"
                
                # 基线标准根据文件类型区分
                if file == "/etc/shadow":
                    baseline_perm = "600"
                else:
                    baseline_perm = "644"
                
                check_results[file] = {
                    "实际值": {
                        "文件权限": perm,
                        "不可变属性": immutable
                    },
                    "基线标准": {
                        "文件权限": f"应设置为{baseline_perm}",
                        "不可变属性": "建议设置不可变属性（防止未授权修改）"
                    },
                    "是否符合": {
                        "文件权限": "符合" if perm == baseline_perm else "不符合",
                        "不可变属性": "符合" if immutable == "是" else "不符合（可选）"
                    }
                }
            
            return check_results
        except Exception as e:
            return {"error": str(e)}

    # 整合安全策略检测
    def check_security_policy():
        try:
            return {
                "dangerous_files": check_dangerous_files(),
                "important_files_tamper": check_important_files_tamper()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data

