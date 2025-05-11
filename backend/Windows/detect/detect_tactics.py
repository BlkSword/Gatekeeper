# 动态策略检测
# 检测内容：密码复杂度、账户锁定策略、空密码账户、Guest账户状态、管理员账户重命名、UAC设置

import winreg
import subprocess

# 将嵌套函数提升为模块级函数
def check_password_complexity():
    """检测密码复杂度策略"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Lsa', 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        value, _ = winreg.QueryValueEx(key, 'PasswordComplexity')
        return {'name': '密码复杂度', 'status': '已启用' if value == 1 else '已禁用', 
                'risk': '低' if value == 1 else '高', 'suggestion': '建议启用密码复杂度策略'}
    except Exception as e:
        return {'name': '密码复杂度', 'error': str(e)}

def check_account_lockout_policy():
    """检测账户锁定策略"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Lsa', 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        threshold, _ = winreg.QueryValueEx(key, 'LockoutThreshold')
        return {'name': '账户锁定策略', 'status': f'锁定阈值：{threshold}次', 
                'risk': '低' if threshold <= 5 else '高', 'suggestion': '建议设置锁定阈值≤5次'}
    except Exception as e:
        return {'name': '账户锁定策略', 'error': str(e)}

def check_empty_password_accounts():
    """检测空密码账户"""
    try:
        result = subprocess.run(['net', 'user'], capture_output=True, text=True, shell=True, encoding='gbk')
        # 改进的用户名提取逻辑
        users = []
        for line in result.stdout.split('\n'):
            parts = line.strip().split()
            if len(parts) > 0 and 'User accounts' not in line:
                users.append(parts[0])
        empty_pass_users = []
        for user in users:
            check = subprocess.run(['net', 'user', user], capture_output=True, text=True, shell=True)
            if 'Password required     No' in check.stdout:
                empty_pass_users.append(user)
        status = f'存在{len(empty_pass_users)}个空密码账户' if empty_pass_users else '未发现空密码账户'
        return {'name': '空密码账户', 'status': status, 'risk': '高' if empty_pass_users else '低',
                'suggestion': '建议删除或设置所有账户密码'}
    except Exception as e:
        return {'name': '空密码账户', 'error': str(e)}

def check_guest_account():
    """检测Guest账户状态"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                        r'SYSTEM\CurrentControlSet\Control\Lsa')
        value, _ = winreg.QueryValueEx(key, 'LimitBlankPasswordUse')
        return {'name': 'Guest账户', 'status': '已禁用' if value == 0 else '已启用',
                'risk': '高' if value == 0 else '低', 'suggestion': '建议禁用Guest账户'}
    except Exception as e:
        return {'name': 'Guest账户', 'error': str(e)}

def check_admin_rename():
    """检测管理员账户重命名"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                        r'SAM\SAM\Domains\Account\Users\Names')
        admin_exists = False
        for i in range(winreg.QueryInfoKey(key)[0]):
            name = winreg.EnumKey(key, i)
            if name.lower() == 'administrator':
                admin_exists = True
                break
        return {'name': '管理员账户重命名', 'status': '未重命名' if admin_exists else '已重命名',
                'risk': '高' if admin_exists else '低', 'suggestion': '建议重命名默认管理员账户'}
    except Exception as e:
        return {'name': '管理员账户重命名', 'error': str(e)}

def check_uac_settings():
    """检测UAC设置"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                        r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System')
        enable_lua, _ = winreg.QueryValueEx(key, 'EnableLUA')
        consent, _ = winreg.QueryValueEx(key, 'ConsentPromptBehaviorAdmin')
        status = []
        status.append('UAC已启用' if enable_lua == 1 else 'UAC已禁用')
        status.append(f'管理员批准模式：{consent}')
        return {'name': 'UAC设置', 'status': ' | '.join(status),
                'risk': '低' if enable_lua == 1 and consent == 2 else '高',
                'suggestion': '建议启用UAC并设置管理员批准模式为2'}
    except Exception as e:
        return {'name': 'UAC设置', 'error': str(e)}

def get_detect_tactics():
    """获取所有安全策略检测结果"""
    return [
        check_password_complexity(),
        check_account_lockout_policy(),
        check_empty_password_accounts(),
        check_guest_account(),
        check_admin_rename(),
        check_uac_settings()
    ]