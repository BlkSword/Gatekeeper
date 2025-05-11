# 文件系统检测
# 检测内容有：磁盘格式、默认共享

import platform
import subprocess
import re
import socket

def get_rules_file():
    # 获取基础信息
    hostname = platform.node()
    domain = socket.getfqdn().split('.', 1)[1] if '.' in socket.getfqdn() else "N/A"

    # 磁盘格式检测（NTFS）
    def check_disk_format():
        try:
            # 使用wmic命令获取磁盘文件系统信息
            disk_output = subprocess.getoutput('wmic logicaldisk get name,filesystem')
            # 解析输出（过滤标题行和空行，提取磁盘名和文件系统）
            disks = []
            for line in disk_output.split('\n'):
                line = line.strip()
                if line and not line.startswith('Name'):  # 跳过标题行
                    parts = re.split(r'\s+', line, 1)  # 按至少一个空格分割
                    if len(parts) == 2:
                        disk_name, fs = parts
                        disks.append({"磁盘": disk_name, "文件系统": fs})
            
            # 提取所有本地磁盘的文件系统（排除无文件系统的情况，如可移动存储）
            ntfs_disks = [d for d in disks if d["文件系统"] == "NTFS" and d["磁盘"] in ['C:', 'D:', 'E:', 'F:']]
            non_ntfs_disks = [d for d in disks if d["文件系统"] != "NTFS" and d["磁盘"] in ['C:', 'D:', 'E:', 'F:']]
            
            return {
                "实际值": {
                    "NTFS磁盘": [d["磁盘"] for d in ntfs_disks],
                    "非NTFS磁盘": [d["磁盘"] for d in non_ntfs_disks]
                },
                "基线标准": "所有本地磁盘（C:、D:等）应使用NTFS文件系统",
                "是否符合": "符合" if not non_ntfs_disks else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 默认共享检测（C$、ADMIN$等）
    def check_default_shares():
        try:
            # 使用net share命令获取所有共享
            share_output = subprocess.getoutput('net share')
            # 提取共享名称（匹配以$结尾的默认共享，如C$、ADMIN$）
            default_shares = re.findall(r'(\w+\$)\s+', share_output)
            
            return {
                "实际值": default_shares,
                "基线标准": "应禁用C$、D$、ADMIN$等默认共享",
                "是否符合": "符合" if not default_shares else "不符合"
            }
        except Exception as e:
            return {"error": str(e)}

    # 整合安全策略检测
    def check_security_policy():
        try:
            return {
                "disk_format": check_disk_format(),
                "default_shares": check_default_shares()
            }
        except Exception as e:
            return {"error": str(e)}

    config_data = {
        "hostname": hostname,
        "domain": domain,
        "security_policy": check_security_policy()
    }
    
    return config_data