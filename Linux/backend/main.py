# uvicorn main:app --reload 

import sqlite3  
import os  
import time
import logging
import traceback
import json


from fastapi import FastAPI, Request, Query ,Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from logging.handlers import RotatingFileHandler


from rules.rules_account import get_rules_account
from rules.rules_authorized import get_rules_authorized
from rules.rules_file import get_rules_file
from rules.rules_kernel import get_rules_kernel
from rules.rules_log import get_rules_log
from rules.rules_other import get_rules_other
from rules.rules_permissions import get_rules_permissions
from rules.rules_service import get_rules_service

from system.system_status import check_internet
from system.system_network import get_network_status
from system.system_process import get_process_info
from system.system_running import get_running_processes
from system.system_traffic import get_system_traffic

from detect.detect_account import get_detect_account
from detect.detect_file import get_detect_file
from detect.detect_network import get_detect_network
from detect.detect_serve import get_detect_serve

from other.health_check import get_health_check


DB_PATH = './database/system.db'
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
DB_DO = './database/detect.db'
os.makedirs(os.path.dirname(DB_DO), exist_ok=True)
DB_Rules = './database/rules.db'  # 新增规则数据库路径
os.makedirs(os.path.dirname(DB_Rules), exist_ok=True)


app = FastAPI()


# 通用数据库操作函数
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


# 应用启动时初始化数据库表
# 系统相关表
create_table(DB_PATH, "system_status")
create_table(DB_PATH, "system_network")
create_table(DB_PATH, "system_process")
create_table(DB_PATH, "system_running")

# 检测相关表（匹配Linux现有检测接口）
create_table(DB_DO, "detect_account")
create_table(DB_DO, "detect_file")
create_table(DB_DO, "detect_network")
create_table(DB_DO, "detect_serve")

create_table(DB_Rules, "rules_account")
create_table(DB_Rules, "rules_authorized")
create_table(DB_Rules, "rules_file")
create_table(DB_Rules, "rules_kernel")
create_table(DB_Rules, "rules_log")
create_table(DB_Rules, "rules_other")
create_table(DB_Rules, "rules_permissions")
create_table(DB_Rules, "rules_service")

request_stats = {"total_requests": 0, "avg_response_time": 0.0}


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
@app.get("/health", tags=["System"])
def health_check():
    return get_health_check()

# 获取流量信息
@app.get("/system_traffic", tags=["System"])
def system_traffic():
    return get_system_traffic()

# 获取系统使用情况
@app.get("/system_status", tags=["System"])
def system_status():
    data = check_internet()
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
    data = get_process_info()  
    insert_data_to_table(DB_PATH, "system_process", data)
    return data

# 获取正在运行的进程信息
@app.get("/system_running", tags=["System"])
def system_running():
    data = get_running_processes()
    insert_data_to_table(DB_PATH, "system_running", data)
    return data


##########################——————————————————实时检测层——————————————————##########################

# 账号策略监控
@app.get("/detect_account", tags=["Detect"])
def detect_account():
    data = get_detect_account()
    insert_data_to_table(DB_DO, "detect_account", data)
    return data

# 文件权限监控
@app.get("/detect_file", tags=["Detect"])
def detect_file():
    data = get_detect_file()
    insert_data_to_table(DB_DO, "detect_file", data)
    return data

# 网络配置监控
@app.get("/detect_network", tags=["Detect"])
def detect_network():
    data = get_detect_network()
    insert_data_to_table(DB_DO, "detect_network", data)
    return data

# 服务状态监控
@app.get("/detect_serve", tags=["Detect"])
def detect_serve():
    data = get_detect_serve()
    insert_data_to_table(DB_DO, "detect_serve", data)
    return data


##########################——————————————————规则检测层——————————————————##########################

# 函数映射字典
rule_functions = {
    "rules_account": get_rules_account,
    "rules_authorized": get_rules_authorized,
    "rules_file": get_rules_file,
    "rules_kernel": get_rules_kernel,
    "rules_log": get_rules_log,
    "rules_other": get_rules_other,
    "rules_permissions": get_rules_permissions,
    "rules_service": get_rules_service
}


@app.post("/rules", tags=["Rules"])
def rules(id: str = Query(..., description="规则ID参数，如rules_account")):  
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



##########################——————————————————其他接口——————————————————##########################

@app.post("/login", tags=["Auth"])
def get_login(credentials: dict = Body(...)):
    username = credentials.get("username")
    password = credentials.get("password")
    
    config_path = os.path.join(os.path.dirname(__file__), "database", "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        correct_username = config.get("username")
        correct_password = config.get("password")
        
        if not (correct_username and correct_password):
            return JSONResponse(
                status_code=500,
                content={"detail": "配置文件缺少username或password字段"}
            )
            
        if username == correct_username and password == correct_password:
            return JSONResponse(
                status_code=200,
                content={"token": "mock-token", "success": True}
            )
        return JSONResponse(
            status_code=401,
            content={"detail": "用户名或密码错误"}
        )
    except FileNotFoundError:
        return JSONResponse(
            status_code=500,
            content={"detail": "配置文件不存在"}
        )
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=500,
            content={"detail": "配置文件格式错误"}
        )


