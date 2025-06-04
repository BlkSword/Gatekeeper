# 账户策略检测
# 检测内容：root账户直接登录、空密码账户、密码复杂度、密码有效期、sudo权限配置
# 系统用户状态、非特权用户权限、密码历史记录


import subprocess
import re
from typing import Dict, Any

def check_root_login() -> Dict[str, Any]:
    """检测root账户是否允许直接登录"""
    try:
        with open("/etc/ssh/sshd_config", "r") as f:
            content = f.read()
        permit_root = re.search(r"^PermitRootLogin\s+(\w+)", content, re.MULTILINE)
        if permit_root:
            return {"检测项": "root直接登录", "状态": "允许" if permit_root.group(1) == "yes" else "禁止", "详情": f"配置值：{permit_root.group(1)}"}
        return {"检测项": "root直接登录", "状态": "异常", "详情": "未找到PermitRootLogin配置"}
    except Exception as e:
        return {"检测项": "root直接登录", "状态": "失败", "详情": f"读取配置文件失败：{str(e)}"}

def check_empty_password() -> Dict[str, Any]:
    """检测空密码账户"""
    try:
        result = subprocess.run(["sudo", "cat", "/etc/shadow"], capture_output=True, text=True, check=True)
        empty_users = [line.split(":")[0] for line in result.stdout.splitlines() if line.split(":")[1] in ["!", "*", ""]]
        return {"检测项": "空密码账户", "状态": "正常" if not empty_users else "异常", "详情": f"空密码账户列表：{empty_users}" if empty_users else "无空密码账户"}
    except Exception as e:
        return {"检测项": "空密码账户", "状态": "失败", "详情": f"执行命令失败：{str(e)}"}

def check_password_complexity() -> Dict[str, Any]:
    """检测密码复杂度策略"""
    try:
        with open("/etc/security/pwquality.conf", "r") as f:
            content = f.read()
        minlen = re.search(r"^minlen\s+(\d+)", content, re.MULTILINE)
        minclass = re.search(r"^minclass\s+(\d+)", content, re.MULTILINE)
        return {
            "检测项": "密码复杂度",
            "状态": "正常" if minlen and minclass else "异常",
            "详情": f"最小长度：{minlen.group(1) if minlen else '未配置'}, 最少字符类型：{minclass.group(1) if minclass else '未配置'}"
        }
    except Exception as e:
        return {"检测项": "密码复杂度", "状态": "失败", "详情": f"读取配置文件失败：{str(e)}"}

def check_password_expiry() -> Dict[str, Any]:
    """检测密码有效期"""
    try:
        result = subprocess.run(["chage", "-l", "root"], capture_output=True, text=True)
        max_days = re.search(r"Maximum password age\s+:\s+(\d+)", result.stdout)
        return {
            "检测项": "密码有效期",
            "状态": "正常" if max_days else "异常",
            "详情": f"最大有效期：{max_days.group(1) if max_days else '未配置'}"
        }
    except Exception as e:
        return {"检测项": "密码有效期", "状态": "失败", "详情": f"执行命令失败：{str(e)}"}

def check_sudo_config() -> Dict[str, Any]:
    """检测sudo权限配置"""
    try:
        with open("/etc/sudoers", "r") as f:
            content = f.read()
        sudo_users = re.findall(r"^(\w+)\s+ALL=\(ALL\)\s+ALL", content, re.MULTILINE)
        return {"检测项": "sudo权限配置", "状态": "正常" if sudo_users else "无额外sudo用户", "详情": f"sudo用户列表：{sudo_users}"}
    except Exception as e:
        return {"检测项": "sudo权限配置", "状态": "失败", "详情": f"读取配置文件失败：{str(e)}"}

def check_system_users() -> Dict[str, Any]:
    """检测系统用户状态"""
    try:
        with open("/etc/passwd", "r") as f:
            users = [line.split(":")[0] for line in f.readlines()]
        return {"检测项": "系统用户状态", "状态": "正常", "详情": f"当前系统用户数：{len(users)}"}
    except Exception as e:
        return {"检测项": "系统用户状态", "状态": "失败", "详情": f"读取用户文件失败：{str(e)}"}

def check_non_privileged_users() -> Dict[str, Any]:
    """检测非特权用户权限"""
    try:
        result = subprocess.run(["getent", "passwd"], capture_output=True, text=True, check=True)
        non_priv_users = [line.split(":")[0] for line in result.stdout.splitlines() if int(line.split(":")[2]) >= 1000]
        return {"检测项": "非特权用户权限", "状态": "正常", "详情": f"非特权用户数：{len(non_priv_users)}"}
    except Exception as e:
        return {"检测项": "非特权用户权限", "状态": "失败", "详情": f"执行命令失败：{str(e)}"}

def check_password_history() -> Dict[str, Any]:
    """检测密码历史记录"""
    try:
        with open("/etc/security/opasswd", "r") as f:
            history_count = len(f.readlines())
        return {"检测项": "密码历史记录", "状态": "正常" if history_count > 0 else "无历史记录", "详情": f"密码历史记录数：{history_count}"}
    except Exception as e:
        return {"检测项": "密码历史记录", "状态": "失败", "详情": f"读取历史文件失败：{str(e)}"}

def get_detect_account() -> Dict[str, Any]:
    """入口方法：执行所有账户策略检测并返回结果"""
    detect_results = {
        "root直接登录检测": check_root_login(),
        "空密码账户检测": check_empty_password(),
        "密码复杂度检测": check_password_complexity(),
        "密码有效期检测": check_password_expiry(),
        "sudo权限配置检测": check_sudo_config(),
        "系统用户状态检测": check_system_users(),
        "非特权用户权限检测": check_non_privileged_users(),
        "密码历史记录检测": check_password_history()
    }
    return {"检测类型": "账户策略检测", "检测结果": detect_results}

