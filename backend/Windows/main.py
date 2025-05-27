# uvicorn main:app --reload

import sqlite3
import time
import logging
import traceback
import os
import json
import uuid


from fastapi import FastAPI, Request, Query ,Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks, HTTPException

from pydantic import BaseModel  
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler

from database import init_db
from models import Rule, Task, TaskResult
from schemas import RuleCreate, RuleUpdate
from rules_executor import run_security_checks

# 系统模块导入
from system.system_status import check_system_status
from system.system_network import get_network_status
from system.system_process import get_process_info
from system.system_running import get_running_processes
from system.system_traffic import get_system_traffic

# 检测模块导入
from detect.detect_tactics import get_detect_tactics
from detect.detect_start import get_detect_start
from detect.detect_telnet import get_detect_telnet
from detect.detect_update import get_detect_update

# 其他模块导入
from other.health_check import get_health_check


class QueryRequest(BaseModel):
    db_type: str
    table_name: str
    where: Optional[Dict[str, Any]] = None

app = FastAPI()

# 规则相关表创建
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


request_stats = {"total_requests": 0, "avg_response_time": 0.0}

# 保留规则层数据库插入函数
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

# 查询函数
def query_data_from_table(db_path: str, table_name: str, where: dict = None):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        query = f"SELECT * FROM {table_name}"
        if where:
            where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])
            query += f" WHERE {where_clause}"
        cursor.execute(query, tuple(where.values()) if where else ())
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return {"columns": columns, "data": rows}
    except Exception as e:
        logger.error(f"查询 {table_name} 失败: {str(e)}\n{traceback.format_exc()}")
        return {"error": str(e)}
    finally:
        conn.close()

# 日志配置
log_handler = RotatingFileHandler('./app.log', maxBytes=1024*1024*5, backupCount=3)
logging.basicConfig(
    handlers=[log_handler],
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    await init_db()

# 请求统计中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
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
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

##########################——————————————————主机检测层——————————————————##########################

# 健康检查接口
@app.get("/health", tags=["Other"])
def health_check():
    return get_health_check()

# 获取系统使用情况
@app.get("/system_status", tags=["System"])
def system_status():
    return check_system_status()

# 获取流量信息
@app.get("/system_traffic", tags=["System"])
def system_traffic():
    return get_system_traffic()

# 获取系统网络信息
@app.get("/system_network", tags=["System"])
def system_network():
    return get_network_status()

# 获取服务与进程信息
@app.get("/system_process", tags=["System"])
def system_process():
    return get_process_info()

# 获取正在运行的进程信息
@app.get("/system_running", tags=["System"])
def system_running():
    return get_running_processes()

##########################——————————————————实时检测层——————————————————##########################

# 策略监控层
@app.get("/detect_tactics", tags=["Detect"])
def detect_tactics():
    return get_detect_tactics()

# 服务启动检测
@app.get("/detect_start", tags=["Detect"])
def detect_start():
    return get_detect_start()

# 网络配置检测
@app.get("/detect_telnet", tags=["Detect"])
def detect_telnet():
    return get_detect_telnet()

# 更新检测
@app.get("/detect_update", tags=["Detect"])
def detect_update():
    return get_detect_update()

##########################——————————————————规则检测层——————————————————##########################

# 创建规则接口
@app.post("/rules", tags=["Rules"])
async def create_rule(rule: RuleCreate):
    """创建新的检测规则"""
    db_rule = await Rule.create(**rule.dict())
    return db_rule

# 获取所有规则接口
@app.get("/rules", tags=["Rules"])
async def get_all_rules():
    """获取所有已配置的检测规则"""
    return await Rule.all()

# 启动检测任务接口
@app.post("/scan", tags=["Rules"])
async def start_scan(background_tasks: BackgroundTasks):
    """启动异步安全检测任务"""
    task_id = str(uuid.uuid4())
    total_rules = await Rule.all().count()
    await Task.create(
        id=task_id,
        status="pending",
        total=total_rules
    )
    background_tasks.add_task(run_security_checks, task_id)
    return {"task_id": task_id, "message": "检测任务已启动"}

# 获取任务进度接口
@app.get("/scan/{task_id}/progress", tags=["Rules"])
async def get_task_progress(task_id: str):
    """获取检测任务进度"""
    task = await Task.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {
        "task_id": task_id,
        "status": task.status,
        "progress": task.progress,
        "total": task.total
    }

# 获取检测结果接口
@app.get("/scan/{task_id}/results", tags=["Rules"])
async def get_task_results(task_id: str):
    """获取检测任务详细结果"""
    results = await TaskResult.filter(task_id=task_id).prefetch_related("rule")
    return [
        {
            "rule_name": result.rule.name,
            "output": json.loads(result.output),
            "compliant": result.is_compliant,
            "baseline": result.rule.baseline_standard
        } for result in results
    ]

# 删除规则接口
@app.get("/rules/delete/{name}", tags=["Rules"])
async def delete_rule(name: str):
    """通过名称删除检测规则（使用 GET 方法）"""
    deleted_count = await Rule.filter(name=name).delete()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="规则不存在")
    return {"status": "success"}


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
