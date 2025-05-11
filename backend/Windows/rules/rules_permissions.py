# 权限规则相关检测
# 检测内容：可远程访问的注册表路径、从远程系统强制关机权限、取得文件所有权权限

import subprocess
import re
import platform
import socket

def get_rules_permissions():
    # 获取基础信息
    hostname = platform.node()
    domain = socket.getfqdn().split('.', 1)[1] if '.' in socket.getfqdn() else "N/A"

    # 可远程访问的注册表路径检测
    def check_remote_registry():
        try:
            # 查询远程注册表访问路径（HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System）
            reg_output = subprocess.getoutput('reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v RemoteRegAccessPaths')
            paths_match = re.search(r'RemoteRegAccessPaths\s+REG_MULTI_SZ\s+(.+)', reg_output)
            actual_paths = paths_match.group(1).split('\\0') if paths_match else "未配置"
            
            return {
                "实际值": actual_paths,
                "基线标准": "应仅允许必要的注册表路径被远程访问（如无特殊需求建议禁用）",
                "是否符合": "符合" if (actual_paths == "未配置" or len(actual_paths) <= 2) else "不符合"  # 假设最多允许2个必要路径
            }
        except Exception as e:
            return {"error": str(e)}

    # 从远程系统强制关机权限检测（SeRemoteShutdownPrivilege）
    def check_remote_shutdown_privilege():
        try:
            priv_output = subprocess.getoutput('whoami /priv')
            has_privilege = "SeRemoteShutdownPrivilege" in priv_output and "Enabled" in priv_output
            
            return {
                "实际值": "已启用" if has_privilege else "未启用",
                "基线标准": "应仅授权给管理员账户，普通用户禁止启用此权限",
                "是否符合": "符合" if not has_privilege else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 取得文件所有权权限检测（SeTakeOwnershipPrivilege）
    def check_take_ownership_privilege():
        try:
            priv_output = subprocess.getoutput('whoami /priv')
            has_privilege = "SeTakeOwnershipPrivilege" in priv_output and "Enabled" in priv_output
            
            return {
                "实际值": "已启用" if has_privilege else "未启用",
                "基线标准": "应仅授权给管理员账户，普通用户禁止启用此权限",
                "是否符合": "符合" if not has_privilege else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合所有检测结果
    config_data = {
        "hostname": hostname,
        "domain": domain,
        "permissions_check": {
            "remote_registry_paths": check_remote_registry(),
            "remote_shutdown_privilege": check_remote_shutdown_privilege(),
            "take_ownership_privilege": check_take_ownership_privilege()
        }
    }
    
    return config_data