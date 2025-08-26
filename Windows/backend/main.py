# BY BlkSword
# uvicorn main:app --reload

import asyncio
from datetime import datetime
import sqlite3
import time
import logging
import traceback
import os
import json
import uuid

from fastapi import FastAPI, Request, Query, Body, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks

from pydantic import BaseModel
from tortoise import Tortoise
from typing import List, Optional, Dict, Any
from logging.handlers import RotatingFileHandler

from baseline.tasks.background_tasks import collect_metrics
from asyncio import create_task

from rules.rules_models import Rule, Task, TaskResult
from rules.schemas import RuleCreate, RuleUpdate
from rules.rules_executor import run_security_checks
from rules.rules_executor import run_single_security_check

# 系统模块导入
from system.system_status import check_system_status
from system.system_network import get_network_status
from system.system_process import get_process_info
from system.system_running import get_running_processes
from system.system_traffic import get_system_traffic

# 基线检测模块导入
from baseline.baseline_routes import router as baseline_router

# 其他模块导入
from other.health_check import get_health_check
from alert.alert_service import send_email_alert

# 全局变量 - 监控任务
monitor_task = None

class QueryRequest(BaseModel):
    db_type: str
    table_name: str
    where: Optional[Dict[str, Any]] = None

class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class AlertConfigUpdate(BaseModel):
    host_server: Optional[str] = None
    sender_qq: Optional[str] = None
    pwd: Optional[str] = None
    receiver: Optional[List[str]] = None
    mail_title: Optional[str] = None
    mail_content: Optional[str] = None

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

# 数据库启动和关闭事件
@app.on_event("startup")
async def startup_event():
    # 配置多数据库连接
    await Tortoise.init(
        config={
            "connections": {
                "rules_db": "sqlite://database/security_check.db",
                "baseline_db": "sqlite://database/baseline.db"
            },
            "apps": {
                "rules_app": {
                    "models": ["rules.rules_models"],
                    "default_connection": "rules_db"
                },
                "baseline_app": {
                    "models": ["baseline.database.base_models"],
                    "default_connection": "baseline_db"
                }
            }
        }
    )
    # 为所有连接生成表结构（或指定具体连接名）
    await Tortoise.generate_schemas()

    # 启动后台任务
    logger.info("Start a scheduled task...")
    app.state.metrics_task = create_task(collect_metrics())


@app.on_event("shutdown")
async def shutdown_event():
    await Tortoise.close_connections()

    if hasattr(app.state, "metrics_task"):
        logger.info("Cancel a scheduled task...")
        app.state.metrics_task.cancel()
        try:
            await app.state.metrics_task
        except asyncio.CancelledError:
            logger.info("The scheduled task has been successfully canceled")


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


# ========== 主机检测层 ==========

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

# ========== 动态检测层 ==========

app.include_router(baseline_router)  # 注册基线路由

# 检测任务控制接口
@app.get("/metrics-task-control", tags=["baseline"])
async def control_metrics_task(action: Optional[str] = Query(None)):
    # 返回当前状态
    if action is None:
        if hasattr(app.state, "metrics_task"):
            if not app.state.metrics_task.done():
                return {"status": "Task is running"}
            return {"status": "Task exists but is not running"}
        return {"status": "Task not found"}

    if action == "start":
        if not hasattr(app.state, "metrics_task") or app.state.metrics_task.done():
            app.state.metrics_task = create_task(collect_metrics())
            return {"status": "Metrics task started"}
        return {"status": "Task already running"}

    elif action == "stop":
        if hasattr(app.state, "metrics_task"):
            app.state.metrics_task.cancel()
            del app.state.metrics_task
            return {"status": "Metrics task stopped"}
        return {"status": "Task not found"}

    elif action == "restart":
        if hasattr(app.state, "metrics_task"):
            app.state.metrics_task.cancel()
        app.state.metrics_task = create_task(collect_metrics())
        return {"status": "Metrics task restarted"}

    else:
        raise HTTPException(status_code=400, detail="Invalid action")

# ========== 告警任务接口 ==========

# 获取阈值配置
def get_threshold(metric_name):
    threshold_path = os.path.join(os.path.dirname(__file__), "alert", "threshold.json")
    try:
        with open(threshold_path, "r") as f:
            thresholds = json.load(f)
            return thresholds.get(metric_name, {}).get("threshold", 3)  # 默认阈值3
    except Exception as e:
        logger.error(f"读取阈值配置失败: {str(e)}")
        return 3

# 异常序列检测函数
def detect_anomaly_sequence(records):
    count = 0
    for record in records:
        if record["is_anomaly"]:
            count += 1
        else:
            count = 0
        if count >= get_threshold(record["metric_name"]):
            return True, count
    return False, count


# 监控任务主函数
async def monitor_anomalies():
    from baseline.model.ewm_model import BaselineHistory
    from backend.alert.alert_service import send_email_alert
    
    while True:
        try:
            # 获取所有指标
            all_metrics = await BaselineHistory.all().distinct().values_list("metric_name", flat=True)

            for metric_name in all_metrics:
                # 获取最新10条记录
                anomaly_records = await BaselineHistory.filter(
                    metric_name=metric_name
                ).order_by("-timestamp").limit(10).values("timestamp", "is_anomaly", "metric_name")

                # 检测异常序列
                is_alert, count = detect_anomaly_sequence(anomaly_records)

                if is_alert:
                    alert_message = f"{metric_name} 检测到连续 {count} 次异常"
                    logger.warning(alert_message)
                    
                    # 直接发送邮件告警
                    success, result = await asyncio.get_event_loop().run_in_executor(
                        None, send_email_alert, alert_message
                    )
                    if not success:
                        logger.error(f"邮件告警失败: {result}")

            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"监控任务异常: {str(e)}")
            await asyncio.sleep(60)
# 监控任务控制路由
@app.get("/anomaly-monitor-control", tags=["baseline"])
async def control_monitor_task(action: Optional[str] = Query(None)):
    global monitor_task

    # 返回当前状态
    if action is None:
        if monitor_task and not monitor_task.done():
            return {"status": "Monitor task is running"}
        return {"status": "Monitor task not running"}

    if action == "start":
        if not monitor_task or monitor_task.done():
            monitor_task = asyncio.create_task(monitor_anomalies())
            return {"status": "Anomaly monitor task started"}
        return {"status": "Task already running"}

    elif action == "stop":
        if monitor_task and not monitor_task.done():
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
            monitor_task = None
            return {"status": "Anomaly monitor task stopped"}
        return {"status": "Task not found"}

    elif action == "restart":
        if monitor_task and not monitor_task.done():
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass

        monitor_task = asyncio.create_task(monitor_anomalies())
        return {"status": "Anomaly monitor task restarted"}

    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    

# 告警配置接口
@app.post("/update_alert_config", tags=["Auth"])
def update_alert_config(config_update: AlertConfigUpdate):
    """更新告警配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), "alert", "alert.json")

    try:
        # 读取现有配置
        with open(config_path, "r", encoding="utf-8") as f:
            current_config = json.load(f)

        # 更新配置项
        for key, value in config_update.dict(exclude_unset=True).items():
            if value is not None:
                current_config[key] = value

        # 写回文件
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(current_config, f, indent=4, ensure_ascii=False)

        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "告警配置更新成功"}
        )

    except FileNotFoundError:
        return JSONResponse(
            status_code=500,
            content={"detail": "告警配置文件不存在"}
        )
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=500,
            content={"detail": "配置文件格式错误"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"配置更新失败: {str(e)}"}
        )
    

# 阈值更新接口
@app.get("/threshold", tags=["Alert"])
async def update_threshold(threshold: int = Query(..., description="新的阈值")):
    """更新阈值配置文件"""
    threshold_path = os.path.join(os.path.dirname(__file__), "alert", "threshold.json")
    
    try:
        # 读取现有配置
        with open(threshold_path, "r") as f:
            thresholds = json.load(f)
        
        # 更新阈值
        thresholds["threshold"] = threshold
        
        # 写回文件
        with open(threshold_path, "w") as f:
            json.dump(thresholds, f, indent=4)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True, 
                "message": "阈值更新成功", 
                "new_threshold": threshold
            }
        )
        
    except FileNotFoundError:
        return JSONResponse(
            status_code=500,
            content={"detail": "阈值配置文件不存在"}
        )
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=500,
            content={"detail": "配置文件格式错误"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"配置更新失败: {str(e)}"}
        )
    
@app.get("/alert_service",tags=["Alert"])
def alert_service():
    return send_email_alert()



# ========== 规则检测层 ==========

# 创建规则接口
@app.post("/rules", tags=["Rules"])
async def create_rule(rule: RuleCreate):
    """创建新的检测规则，若规则名重复则返回错误"""
    existing_rule = await Rule.filter(name=rule.name).first()
    if existing_rule:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "规则名称已存在"}
        )

    try:
        db_rule = await Rule.create(**rule.dict())
        return {"success": True, "data": db_rule}
    except Exception as e:
        logger.error(f"Failed to create rule: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "创建规则失败，请稍后重试"}
        )


# 批量创建规则接口
@app.post("/rules/batch", tags=["Rules"])
async def create_rules(rules: List[RuleCreate]):
    """批量创建检测规则，跳过已存在的规则"""
    results = []
    for rule in rules:
        existing_rule = await Rule.filter(name=rule.name).first()
        if existing_rule:
            results.append({"name": rule.name, "status": "skipped", "message": "规则名称已存在"})
            continue

        try:
            db_rule = await Rule.create(**rule.dict())
            results.append({"name": rule.name, "status": "success", "data": db_rule})
        except Exception as e:
            logger.error(f"Failed to create rule {rule.name}: {str(e)}")
            results.append({"name": rule.name, "status": "failed", "message": str(e)})

    return {"results": results}

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

# 单一规则检测接口
@app.post("/scan/single", tags=["Rules"])
async def start_single_scan(background_tasks: BackgroundTasks, name: str = Body(..., embed=True)):
    """启动异步安全检测任务，仅针对指定名称的规则"""
    # 查询指定名称的规则
    rule = await Rule.filter(name=name).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则未找到")

    task_id = str(uuid.uuid4())
    await Task.create(
        id=task_id,
        status="pending",
        total=1
    )

    # 将规则名称传递给执行函数
    background_tasks.add_task(run_single_security_check, task_id, rule_name=name)
    return {"task_id": task_id, "message": f"检测任务已启动，正在执行规则：{name}"}


# 获取任务进度接口
@app.get("/scan/{task_id}/progress", tags=["Rules"])
async def get_task_progress(task_id: str):
    """获取检测任务进度及合规统计"""
    task = await Task.get_or_none(id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 统计合规与不合规数量
    compliant_count = await TaskResult.filter(task_id=task_id, is_compliant=True).count()
    non_compliant_count = await TaskResult.filter(task_id=task_id, is_compliant=False).count()

    return {
        "task_id": task_id,
        "status": task.status,
        "progress": task.progress,
        "total": task.total,
        "compliant_count": compliant_count,
        "non_compliant_count": non_compliant_count
    }

# 获取检测结果接口
@app.get("/scan/{task_id}/results", tags=["Rules"])
async def get_task_results(task_id: str):
    """获取检测任务详细结果"""
    results = await TaskResult.filter(task_id=task_id).prefetch_related("rule")
    return [
        {
            "rule_name": result.rule.name,
            "compliant": result.is_compliant,
        } for result in results
    ]

# 删除规则接口
@app.get("/rules/delete/{name}", tags=["Rules"])
async def delete_rule(name: str):
    """通过名称删除检测规则"""
    deleted_count = await Rule.filter(name=name).delete()
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="规则不存在")
    return {"status": "success"}

# 查询警告占比接口
@app.get("/non-compliant-rules", tags=["Rules"])
async def get_non_compliant_severity(task_id: str = Query(...)):
    # 查询有效规则结果
    results = await TaskResult.filter(
        task_id=task_id,
        is_compliant=0,
        rule_id__in=await Rule.all().values_list("id", flat=True)
    ).values('rule__severity_level')

    # 初始化统计结构
    counts = {
        "high": 0,
        "medium": 0,
        "low": 0
    }

    # 处理查询结果
    for item in results:
        level = item['rule__severity_level']
        if level in counts:
            counts[level] += 1

    return {
        "task_id": task_id,
        "statistics": {
            "high_risk": {"count": counts["high"]},
            "medium_risk": {"count": counts["medium"]},
            "low_risk": {"count": counts["low"]}
        }
    }

# 获取单个规则参数
@app.post("/rulesfind", tags=["Rules"])
async def get_rule_by_name(name: str = Body(..., embed=True)):
    rule = await Rule.filter(name=name).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    # 返回所有参数字段
    return {
        "id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "rule_type": rule.rule_type,
        "params": rule.params,
        "expected_result": rule.expected_result,
        "baseline_standard": rule.baseline_standard,
        "severity_level": rule.severity_level,
        "created_at": rule.created_at.isoformat() if rule.created_at else None,
        "risk_description": rule.risk_description,
        "solution": rule.solution,
        "tip": rule.tip
    }


# 获取最近一次任务ID接口
@app.get("/last", tags=["Rules"])
async def get_latest_task():
    """通过created_at时间排序获取最新任务ID"""
    latest_task = await Task.all().order_by("-created_at").first()

    if not latest_task:
        raise HTTPException(status_code=404, detail="未找到任何任务记录")

    return {"task_id": latest_task.id}

# 获取最近三次任务记录接口
@app.get("/last-three", tags=["Rules"])
async def get_last_three_tasks():
    """获取最近三次检测任务记录"""
    tasks = await Task.all().order_by("-created_at").limit(3)

    if not tasks:
        raise HTTPException(status_code=404, detail="未找到任何任务记录")

    return [
        {
            "task_id": task.id,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "status": task.status,
            "progress": task.progress,
            "total": task.total
        } for task in tasks
    ]


# ========== 其他接口 ==========

# 登录接口
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

# 修改密码接口
@app.post("/update_password", tags=["Auth"])
def update_password(request: UpdatePasswordRequest):
    config_path = os.path.join(os.path.dirname(__file__), "database", "config.json")

    try:
        # 读取现有配置
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # 验证原密码
        if config.get("password") != request.old_password:
            return JSONResponse(
                status_code=401,
                content={"detail": "原密码验证失败"}
            )

        # 更新密码
        config["password"] = request.new_password

        # 写回文件
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "密码更新成功"}
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
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"密码更新失败: {str(e)}"}
        )




# # 测试
# @app.get("/test", tags=["test"])
# def rules_account():
#     return get_rules_account()