# uvicorn main:app --reload 

import sqlite3
import time
import logging
import traceback
import os


from fastapi import FastAPI, Request, Query 
from fastapi.responses import JSONResponse
from pydantic import BaseModel  # 新增pydantic模型导入

from rules.rules_account import get_rules_account
from rules.rules_log import get_rules_log
from rules.rules_permissions import get_rules_permissions
from rules.rules_protocols import get_rules_protocols
from rules.rules_service import get_rules_service
from rules.rules_file import get_rules_file
from rules.rules_patch import get_rules_patch
from rules.rules_other import get_rules_other

from system.system_status import check_system_status
from system.system_network import get_network_status
from system.system_process import get_process_info
from system.system_running import get_running_processes

from detect.detect_tactics import get_detect_tactics
from detect.detect_start import get_detect_start
from detect.detect_telnet import get_detect_telnet
from detect.detect_update import get_detect_update

from other.health_check import get_health_check

from logging.handlers import RotatingFileHandler



DB_PATH = './database/system.db'
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
DB_DO = './database/detect.db'
os.makedirs(os.path.dirname(DB_DO), exist_ok=True)
DB_Rules = './database/rules.db'
os.makedirs(os.path.dirname(DB_Rules), exist_ok=True)


app = FastAPI()


# 创建系统状态数据表
# 通用表创建函数
def create_table(db_path: str, table_name: str):
    """通用创建数据库表函数"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

## 应用启动时初始化数据库表
# 系统相关表
create_table(DB_PATH, "system_status")
create_table(DB_PATH, "system_information")
create_table(DB_PATH, "system_network")
create_table(DB_PATH, "system_process")
create_table(DB_PATH, "system_running")

# 检测相关表
create_table(DB_DO, "detect_tactics")
create_table(DB_DO, "detect_start")
create_table(DB_DO, "detect_telnet")
create_table(DB_DO, "detect_update")

# 规则相关表
create_table(DB_Rules, "rules_account")
create_table(DB_Rules, "rules_log")
create_table(DB_Rules, "rules_permissions")
create_table(DB_Rules, "rules_protocols")
create_table(DB_Rules, "rules_service")
create_table(DB_Rules, "rules_file")
create_table(DB_Rules, "rules_patch")
create_table(DB_Rules, "rules_other")


request_stats = {"total_requests": 0, "avg_response_time": 0.0}


# 提取通用数据库插入函数
def insert_data_to_table(db_path: str, table_name: str, data: any):
    """通用数据库数据插入函数"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO {table_name} (data) VALUES (?)', (str(data),))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"{table_name}数据库插入失败: {str(e)}\n{traceback.format_exc()}")


# 配置日志系统
log_handler = RotatingFileHandler(
    './app.log',
    maxBytes=1024*1024*5,  
    backupCount=3
)
logging.basicConfig(
    handlers=[log_handler],
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 修改中间件增加详细日志记录
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 记录请求日志
        logger.info(
            f"Request: {request.method} {request.url} | " 
            f"Status: {response.status_code} | "
            f"Process Time: {process_time:.4f}s"
        )
        
        request_stats["total_requests"] += 1
        request_stats["avg_response_time"] = (
            (request_stats["avg_response_time"] * (request_stats["total_requests"] - 1) + process_time) 
            / request_stats["total_requests"]
        )
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )



##########################——————————————————主机检测层——————————————————##########################

# 健康检查接口
@app.get("/health", tags=["Other"])
def health_check():
    return get_health_check()

# 获取系统使用情况
@app.get("/system_status", tags=["System"])
def system_status():
    data = check_system_status()
    insert_data_to_table(DB_PATH, "system_status", data)
    return data

# 获取系统网络信息
@app.get("/system_network", tags=["System"])
def system_network():
    data = get_network_status()
    insert_data_to_table(DB_PATH, "system_network", data)
    return data

# 获取服务与进程信息
@app.get("/system_process", tags=["System"])
def system_process():
    data = get_process_info()  # 获取原始数据
    insert_data_to_table(DB_PATH, "system_process", data)
    return data

# 获取正在运行的进程信息
@app.get("/system_running", tags=["System"])
def system_running():
    data = get_running_processes()
    insert_data_to_table(DB_PATH, "system_running", data)
    return data


##########################——————————————————实时检测层——————————————————##########################


# 策略监控层
@app.get("/detect_tactics", tags=["Detect"])
def detect_tactics():
    data = get_detect_tactics()
    insert_data_to_table(DB_DO, "detect_tactics", data)
    return data

# 服务启动检测
@app.get("/detect_start", tags=["Detect"])
def detect_start():
    data = get_detect_start()
    insert_data_to_table(DB_DO, "detect_start", data)
    return data

# 网络配置检测
@app.get("/detect_telnet", tags=["Detect"])
def detect_telnet():
    data = get_detect_telnet()
    insert_data_to_table(DB_DO, "detect_telnet", data)
    return data

# 更新检测
@app.get("/detect_update", tags=["Detect"])
def detect_update():
    data = get_detect_update()
    insert_data_to_table(DB_DO, "detect_update", data)
    return data



##########################——————————————————规则检测层——————————————————##########################

# 函数映射字典
rule_functions = {
    "rules_account": get_rules_account,
    "rules_log": get_rules_log,
    "rules_permissions": get_rules_permissions,
    "rules_protocols": get_rules_protocols,
    "rules_service": get_rules_service,
    "rules_file": get_rules_file,
    "rules_patch": get_rules_patch,
    "rules_other": get_rules_other
}


@app.post("/rules", tags=["Rules"])
def rules(id: str = Query(..., description="规则ID参数，如rules_patch")):  
    # 根据ID获取对应的检测函数
    rule_func = rule_functions.get(id)
    
    if not rule_func:
        return JSONResponse(
            status_code=400,
            content={"detail": f"无效的规则ID: {id}，可选值：{list(rule_functions.keys())}"}
        )
    
    data = rule_func()
    insert_data_to_table(DB_Rules, id, data)
    return data







