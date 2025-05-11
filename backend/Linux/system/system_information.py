# 检测系统配置信息
# 检测内容有：操作系统信息、已安装的更新补丁、系统日志	

import platform
import subprocess
from fastapi.logger import logger
import os

def get_information_info():
    logger.info("Start collecting system information")
    # 获取操作系统信息（Linux适配）
    os_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version()
    }
    # 读取Linux发行版信息（通过/etc/os-release）
    try:
        with open("/etc/os-release", "r") as f:
            os_release = {}
            for line in f:
                if line.strip() and "=" in line:
                    key, value = line.strip().split("=", 1)
                    os_release[key] = value.strip('"')
            os_info.update({
                "distribution": os_release.get("NAME"),
                "distribution_version": os_release.get("VERSION_ID")
            })
    except Exception as e:
        os_info["distribution_error"] = str(e)

    # 获取已安装的更新补丁（支持apt和yum/dnf）
    update_list = []
    try:
        # 检测包管理器类型
        if os.path.exists("/usr/bin/apt"):
            # Debian/Ubuntu系：通过dpkg日志获取最近安装的更新
            cmd = "grep ' install ' /var/log/dpkg.log | tail -n 20 | awk '{print $4,$5}'"
            updates = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True
            ).split('\n')
            for line in updates:
                if line.strip():
                    pkg, version = line.split()[:2]
                    update_list.append({"package": pkg, "version": version, "type": "apt"})
        elif os.path.exists("/usr/bin/yum") or os.path.exists("/usr/bin/dnf"):
            # RedHat系：通过yum日志获取最近安装的更新
            cmd = "tail -n 20 /var/log/yum.log | grep 'Installed:' | awk '{print $2,$3}'"
            updates = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True
            ).split('\n')
            for line in updates:
                if line.strip():
                    pkg, version = line.split()[:2]
                    update_list.append({"package": pkg, "version": version, "type": "yum/dnf"})
        else:
            update_list.append({"error": "Unsupported package manager"})
    except Exception as e:
        update_list = [{"error": str(e)}]

    # 获取系统日志（最近10条）
    system_logs = []
    try:
        log_path = "/var/log/syslog" if os.path.exists("/var/log/syslog") else "/var/log/messages"
        logs = subprocess.check_output(
            f"tail -n 10 {log_path}", shell=True, stderr=subprocess.STDOUT, universal_newlines=True
        ).split('\n')
        system_logs = [line.strip() for line in logs if line.strip()]
    except Exception as e:
        system_logs = [f"Read log error: {str(e)}"]

    return {
        "os_information": os_info,
        "updates": update_list,
        "system_logs": system_logs
    }