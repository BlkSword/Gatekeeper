# 数据库模型定义

from tortoise import fields
from tortoise.models import Model

class BaselineConfig(Model):
    """基线配置表"""
    id = fields.IntField(pk=True)  # 主键ID
    metric_name = fields.CharField(max_length=100, unique=True)  # 指标名称（唯一标识）
    window_size = fields.IntField(default=24)  # 统计窗口大小（小时）
    threshold_sigma = fields.FloatField(default=3.0)  # 异常检测标准差阈值
    enabled = fields.BooleanField(default=True)  # 是否启用该基线配置
    last_updated = fields.DatetimeField(auto_now=True)  # 最后更新时间

    class Meta:
        table = "baseline_config"
        using_db = "baseline_db"  
        app_label = "baseline_app"  

class BaselineHistory(Model):
    """基线历史表"""
    id = fields.IntField(pk=True)  # 主键ID
    metric_name = fields.CharField(max_length=100)  # 关联的指标名称
    timestamp = fields.DatetimeField(auto_now_add=True)  # 记录时间戳
    value = fields.FloatField()  # 原始指标值
    baseline = fields.FloatField()  # 计算出的基线值
    threshold_low = fields.FloatField()  # 下限阈值
    threshold_high = fields.FloatField()  # 上限阈值
    is_anomaly = fields.BooleanField(default=False)  # 是否标记为异常

    class Meta:
        table = "baseline_history"
        using_db = "baseline_db"  
        app_label = "baseline_app"  