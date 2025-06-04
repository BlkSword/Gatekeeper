# 服务状态监控
# 检测内容：SSH服务、Remote Registry、Print Spooler	、Telnet、Apache/Nginx	

import subprocess

def get_detect_serve():
    """检测Linux系统指定服务的运行状态"""
    service_status = {}
    
    # 检测SSH服务（对应Linux服务名：sshd）
    ssh_result = subprocess.run(["systemctl", "is-active", "sshd"], capture_output=True, text=True)
    service_status["SSH服务"] = "运行中" if ssh_result.stdout.strip() == "active" else "未运行"
    
    # 检测Remote Registry（Linux无原生对应服务，假设为自定义服务）
    remote_reg_result = subprocess.run(["systemctl", "is-active", "remote-registry"], capture_output=True, text=True)
    service_status["Remote Registry"] = "运行中" if remote_reg_result.stdout.strip() == "active" else "未运行"
    
    # 检测Print Spooler（Linux对应cups服务）
    print_spool_result = subprocess.run(["systemctl", "is-active", "cups"], capture_output=True, text=True)
    service_status["Print Spooler"] = "运行中" if print_spool_result.stdout.strip() == "active" else "未运行"
    
    # 检测Telnet服务（对应Linux服务名：telnetd）
    telnet_result = subprocess.run(["systemctl", "is-active", "telnetd"], capture_output=True, text=True)
    service_status["Telnet"] = "运行中" if telnet_result.stdout.strip() == "active" else "未运行"
    
    # 检测Apache/Nginx（Apache对应httpd或apache2，Nginx对应nginx）
    apache_result = subprocess.run(["systemctl", "is-active", "httpd"], capture_output=True, text=True)
    nginx_result = subprocess.run(["systemctl", "is-active", "nginx"], capture_output=True, text=True)
    service_status["Apache"] = "运行中" if apache_result.stdout.strip() == "active" else "未运行"
    service_status["Nginx"] = "运行中" if nginx_result.stdout.strip() == "active" else "未运行"
    
    return service_status
