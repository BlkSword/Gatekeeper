# 定时任务采集

import asyncio
from .baseline_status import check_baseline_status
from baseline.model.ewm_model import EWMModel
from baseline.database.base_models import BaselineConfig, BaselineHistory
# from alert.alert_service import trigger_alert
import logging

model_cache = {}
logger = logging.getLogger(__name__)

async def collect_metrics():
    """定时采集指标并更新基线，支持优雅关闭"""
    try:
        while True:
            try:
                # 获取系统指标
                metrics = check_baseline_status()
                
                for metric_name, value in metrics.items():
                    # 获取配置
                    config = await BaselineConfig.get_or_none(
                        metric_name=metric_name, enabled=True
                    )
                    if not config:
                        continue
                    
                    # 初始化模型缓存
                    if metric_name not in model_cache:
                        model_cache[metric_name] = EWMModel(
                            window_size=config.window_size,
                            threshold_sigma=config.threshold_sigma
                        )
                    
                    # 更新基线
                    ewm_model = model_cache[metric_name]
                    is_anomaly, info = ewm_model.detect(value)
                    
                    # 存储历史记录
                    await BaselineHistory.create(
                        metric_name=metric_name,
                        value=value,
                        baseline=info["mean"],
                        threshold_low=info["threshold_low"],
                        threshold_high=info["threshold_high"],
                        is_anomaly=is_anomaly
                    )
                    
                    # # 触发告警
                    # if is_anomaly:
                    #     await trigger_alert(metric_name, value, info)
                        
            except Exception as e:
                logger.error(f"基线采集错误: {str(e)}")
            
            try:
                await asyncio.sleep(30)  # 每30秒采集一次
            except asyncio.CancelledError:
                logger.info("正在停止定时采集任务...")
                # 清理模型缓存
                model_cache.clear()
                raise
                
    except asyncio.CancelledError:
        logger.info("定时任务已成功取消，资源已释放")
        raise