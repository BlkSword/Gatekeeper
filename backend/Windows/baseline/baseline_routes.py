# 路由配置

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

# 本地模块导入
from baseline.model.ewm_model import EWMModel
from baseline.database.base_models import BaselineConfig, BaselineHistory

router = APIRouter(prefix="/baseline", tags=["Baseline"])

# ========== 请求模型 ==========
class BaselineConfigCreate(BaseModel):
    """创建基线配置请求模型"""
    metric_name: str
    window_size: int = 24  # 窗口大小（小时）
    threshold_sigma: float = 3.0  # 异常检测阈值倍数
    enabled: bool = True  # 是否启用

class BaselineConfigUpdate(BaseModel):
    """更新基线配置请求模型"""
    window_size: Optional[int] = None
    threshold_sigma: Optional[float] = None
    enabled: Optional[bool] = None

class BaselineHistoryResponse(BaseModel):
    """历史数据响应模型"""
    timestamp: datetime
    value: float
    baseline: float
    threshold_low: float
    threshold_high: float
    is_anomaly: bool

# ========== 内存缓存 ==========
model_cache = {}  # 缓存实时计算模型 {metric_name: EWMModel}

# ========== 核心路由 ==========
@router.post("/config")
async def create_config(config: BaselineConfigCreate):
    """创建新基线配置并初始化计算模型"""
    try:
        # 创建数据库记录
        db_config = await BaselineConfig.create(**config.dict())
        
        # 初始化内存模型
        model_cache[config.metric_name] = EWMModel(
            window_size=config.window_size,
            threshold_sigma=config.threshold_sigma
        )
        
        return {"success": True, "data": db_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建配置失败: {str(e)}")

@router.get("/config/{metric_name}")
async def get_config(metric_name: str):
    """获取指定指标的基线配置"""
    config = await BaselineConfig.get_or_none(metric_name=metric_name)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return {"success": True, "data": config}

@router.get("/configs")
async def get_all_configs():
    """获取所有基线配置列表"""
    configs = await BaselineConfig.all()
    return {"success": True, "data": configs}

@router.put("/config/{metric_name}")
async def update_config(metric_name: str, config: BaselineConfigUpdate):
    """更新基线配置并同步内存模型"""
    db_config = await BaselineConfig.get_or_none(metric_name=metric_name)
    if not db_config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    try:
        # 更新数据库配置
        update_data = config.dict(exclude_unset=True)
        await db_config.update_from_dict(update_data).save()
        
        # 更新内存模型
        if metric_name in model_cache:
            if "window_size" in update_data:
                model_cache[metric_name].alpha = 2 / (db_config.window_size + 1)
            if "threshold_sigma" in update_data:
                model_cache[metric_name].threshold_sigma = db_config.threshold_sigma
            
        return {"success": True, "data": db_config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")

@router.delete("/config/{metric_name}")
async def delete_config(metric_name: str):
    """删除基线配置并清理内存模型"""
    config = await BaselineConfig.get_or_none(metric_name=metric_name)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    try:
        # 删除数据库记录
        await config.delete()
        
        # 清理内存模型
        if metric_name in model_cache:
            del model_cache[metric_name]
            
        return {"success": True, "message": "配置已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除配置失败: {str(e)}")

# ========== 历史数据查询 ==========
@router.get("/history/{metric_name}")
async def get_history(
    metric_name: str,
    limit: int = Query(100, ge=1, le=1000),  # 默认返回最近100条
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """查询基线历史数据"""
    query = BaselineHistory.filter(metric_name=metric_name)
    
    if start_time:
        query = query.filter(timestamp__gte=start_time)
    if end_time:
        query = query.filter(timestamp__lte=end_time)
    
    history = await query.order_by("-timestamp").limit(limit).all()
    return {"success": True, "data": history}

# 重新最新的五条信息
@router.get("/latest/{metric_name}")
async def get_latest_history(metric_name: str):
    """获取指定指标的最新5条历史数据"""
    try:
        # 查询最新5条记录
        history = await BaselineHistory.filter(
            metric_name=metric_name
        ).order_by("-timestamp").limit(5).all()
        
        return {"success": True, "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最新数据失败: {str(e)}")
    

# 最新异常状态
@router.get("/anomaly-timestamps/{metric_name}")
async def get_anomaly_timestamps(metric_name: str):
    try:
        anomaly_records = await BaselineHistory.filter(
            metric_name=metric_name
        ).order_by("-timestamp").limit(10).values("timestamp", "is_anomaly")
        
        return {"success": True, "data": anomaly_records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取异常时间戳失败: {str(e)}")