# 数据库模型定义

from tortoise import fields
from tortoise.models import Model

class BaselineConfig(Model):
    """基线配置表"""
    id = fields.IntField(pk=True)
    metric_name = fields.CharField(max_length=100, unique=True)
    window_size = fields.IntField(default=24)
    threshold_sigma = fields.FloatField(default=3.0)
    enabled = fields.BooleanField(default=True)
    last_updated = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "baseline_config"

class BaselineHistory(Model):
    """基线历史表"""
    id = fields.IntField(pk=True)
    metric_name = fields.CharField(max_length=100)
    timestamp = fields.DatetimeField(auto_now_add=True)
    value = fields.FloatField()
    baseline = fields.FloatField()
    threshold_low = fields.FloatField()
    threshold_high = fields.FloatField()
    is_anomaly = fields.BooleanField(default=False)

    class Meta:
        table = "baseline_history"