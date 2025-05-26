# Pydantic模型

from pydantic import BaseModel
from typing import Optional, Dict, Union

class RuleCreate(BaseModel):
    name: str
    description: str
    rule_type: str  # 枚举值：command/file/service/registry
    params: Dict    # 规则参数（根据类型不同结构不同）
    expected_result: Dict  # 预期结果（用于判断合规性）
    baseline_standard: str  # 基线标准描述
    severity_level: str  # 枚举值：high/medium/low

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rule_type: Optional[str] = None
    params: Optional[Dict] = None
    expected_result: Optional[Dict] = None
    baseline_standard: Optional[str] = None
    severity_level: Optional[str] = None