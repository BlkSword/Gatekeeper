# Pydantic模型

from pydantic import BaseModel
from typing import Optional, Dict, Union

class RuleCreate(BaseModel):
    name: str
    description: str
    rule_type: str
    params: Dict
    expected_result: Dict
    baseline_standard: str
    severity_level: str
    risk_description: str  
    solution: str          
    tip: str               


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rule_type: Optional[str] = None
    params: Optional[Dict] = None
    expected_result: Optional[Dict] = None
    baseline_standard: Optional[str] = None
    severity_level: Optional[str] = None