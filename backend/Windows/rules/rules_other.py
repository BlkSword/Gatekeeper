# 其他检测
# 检测内容有：屏幕保护程序启用及密码保护​、禁止自动登录​、
# DLL 劫持风险检测（无用户组对系统 DLL 有写权限​）、受控文件夹访问



import platform
import subprocess
import re
import socket
import os
import winreg  # 用于注册表操作

def get_rules_other():
    # 获取基础信息
    hostname = platform.node()
    domain = socket.getfqdn().split('.', 1)[1] if '.' in socket.getfqdn() else "N/A"

    # 屏幕保护程序启用及密码保护检测
    def check_screensaver():
        try:
            # 访问注册表路径
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop")
            # 获取屏幕保护启用状态（1=启用，0=禁用）
            ss_active = winreg.QueryValueEx(key, "ScreenSaveActive")[0]
            # 获取等待时间（秒）
            ss_timeout = winreg.QueryValueEx(key, "ScreenSaveTimeOut")[0]
            # 获取密码保护状态（1=启用，0=禁用）
            ss_secure = winreg.QueryValueEx(key, "ScreenSaverIsSecure")[0]

            return {
                "实际值": {
                    "启用状态": "已启用" if ss_active == "1" else "未启用",
                    "等待时间(秒)": ss_timeout,
                    "密码保护": "已启用" if ss_secure == "1" else "未启用"
                },
                "基线标准": {
                    "启用状态": "应启用屏幕保护程序",
                    "等待时间(秒)": "建议不超过900秒（15分钟）",
                    "密码保护": "应启用密码保护"
                },
                "是否符合": {
                    "启用状态": "符合" if ss_active == "1" else "不符合",
                    "等待时间(秒)": "符合" if int(ss_timeout) <= 900 else "不符合",
                    "密码保护": "符合" if ss_secure == "1" else "不符合"
                }
            }
        except Exception as e:
            return {"error": str(e)}

    # 禁止自动登录检测
    def check_auto_login():
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon")
            # 自动登录启用状态（1=启用，0=禁用）
            auto_logon = winreg.QueryValueEx(key, "AutoAdminLogon")[0]
            # 默认登录密码（空表示无密码）
            default_pwd = winreg.QueryValueEx(key, "DefaultPassword")[0]

            return {
                "实际值": {
                    "自动登录状态": "已启用" if auto_logon == "1" else "未启用",
                    "默认密码": "存在" if default_pwd else "无"
                },
                "基线标准": "应禁用自动登录（AutoAdminLogon=0）且默认密码为空",
                "是否符合": "符合" if auto_logon == "0" and not default_pwd else "不符合"
            }
        except FileNotFoundError:
            return {"实际值": "未配置", "基线标准": "应禁用自动登录", "是否符合": "不符合"}
        except Exception as e:
            return {"error": str(e)}

    # DLL劫持风险检测（系统DLL写权限检查）
    def check_dll_hijack():
        try:
            # 检查System32目录下的DLL权限（示例检查user32.dll）
            dll_path = r"C:\Windows\System32\user32.dll"
            perm_output = subprocess.getoutput(f'icacls "{dll_path}"')
            # 检测是否存在非管理员组的写权限（排除BUILTIN\Administrators）
            has_unsafe_perm = re.search(r"(?<!BUILTIN\\Administrators).*:(?=.*W)", perm_output) is not None

            return {
                "实际值": "存在风险" if has_unsafe_perm else "无风险",
                "基线标准": "系统DLL不应存在非管理员组的写权限",
                "是否符合": "符合" if not has_unsafe_perm else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 受控文件夹访问检测
    def check_controlled_folders():
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows Defender\Windows Defender Exploit Guard\Controlled Folder Access")
            # 受控文件夹访问启用状态（1=启用，0=禁用）
            cf_enabled = winreg.QueryValueEx(key, "EnableControlledFolderAccess")[0]

            return {
                "实际值": "已启用" if cf_enabled == 1 else "未启用",
                "基线标准": "应启用受控文件夹访问",
                "是否符合": "符合" if cf_enabled == 1 else "不符合"
            }
        except FileNotFoundError:
            return {"实际值": "未配置", "基线标准": "应启用受控文件夹访问", "是否符合": "不符合"}
        except Exception as e:
            return {"error": str(e)}

    # 整合所有安全策略检测
    def check_security_policy():
        try:
            return {
                "screensaver": check_screensaver(),
                "auto_login": check_auto_login(),
                "dll_hijack": check_dll_hijack(),
                "controlled_folders": check_controlled_folders()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data