# 磁盘格式检测脚本

import subprocess
import re
import json

def run_check():
    try:
        disk_output = subprocess.getoutput('wmic logicaldisk get name,filesystem')
        disks = []
        for line in disk_output.split('\n'):
            line = line.strip()
            if line and not line.startswith('Name'):
                parts = re.split(r'\s+', line, 1)
                if len(parts) == 2:
                    disk_name, fs = parts
                    disks.append({"磁盘": disk_name, "文件系统": fs})
        
        non_ntfs_disks = [d for d in disks if d["文件系统"] != "NTFS" and d["磁盘"] in ['C:', 'D:', 'E:', 'F:']]
        return {
            "check_name": "磁盘格式检测（NTFS）",
            "status": not bool(non_ntfs_disks)
        }
    except Exception as e:
        return {"check_name": "磁盘格式检测（NTFS）", "status": False, "error": str(e)}
    
if __name__ == "__main__":
    result = run_check()
    print(json.dumps(result, ensure_ascii=False)) 