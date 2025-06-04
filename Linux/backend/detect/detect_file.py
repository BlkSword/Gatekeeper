# 文件权限检测
# 检测内容：/etc/passwd、/etc/shadow、/etc/ssh/sshd_config、
# /etc/crontab、/etc/cron.*、世界可写文件、SUID/SGID文件、/tmp目录权限
import os
import stat
import glob

def get_detect_file():
    """检测Linux系统指定文件/目录的权限"""
    result = {}

    # 检测固定路径文件
    fixed_files = [
        "/etc/passwd",
        "/etc/shadow",
        "/etc/ssh/sshd_config",
        "/etc/crontab"
    ]
    for file_path in fixed_files:
        try:
            st = os.stat(file_path)
            result[file_path] = {
                "mode": oct(st.st_mode & 0o777),  # 获取权限模式（八进制）
                "owner": st.st_uid,
                "group": st.st_gid
            }
        except FileNotFoundError:
            result[file_path] = "文件不存在"

    # 检测/etc/cron.*通配符文件
    cron_files = glob.glob("/etc/cron.*")
    for cron_file in cron_files:
        try:
            st = os.stat(cron_file)
            result[cron_file] = {
                "mode": oct(st.st_mode & 0o777),
                "owner": st.st_uid,
                "group": st.st_gid
            }
        except Exception as e:
            result[cron_file] = f"检测失败: {str(e)}"

    # 检测世界可写文件（遍历根目录，实际使用建议限制目录范围）
    world_writable = []
    for root, dirs, files in os.walk("/"):
        for name in files + dirs:
            path = os.path.join(root, name)
            if os.path.exists(path) and (os.stat(path).st_mode & stat.S_IWOTH):
                world_writable.append(path)
    result["世界可写文件"] = world_writable[:5]  # 示例取前5个，避免结果过长

    # 检测SUID/SGID文件
    suid_sgid_files = []
    for root, dirs, files in os.walk("/"):
        for name in files:
            path = os.path.join(root, name)
            try:
                st = os.stat(path)
                if st.st_mode & (stat.S_ISUID | stat.S_ISGID):
                    suid_sgid_files.append(path)
            except PermissionError:
                continue  # 跳过无权限访问的文件
    result["SUID/SGID文件"] = suid_sgid_files[:5]

    # 检测/tmp目录权限
    try:
        tmp_st = os.stat("/tmp")
        result["/tmp目录权限"] = {
            "mode": oct(tmp_st.st_mode & 0o777),
            "owner": tmp_st.st_uid,
            "group": tmp_st.st_gid
        }
    except Exception as e:
        result["/tmp目录权限"] = f"检测失败: {str(e)}"

    return result