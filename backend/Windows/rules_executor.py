# 规则执行引擎

import subprocess
import json
import re
import hashlib
import winreg
from models import Rule, TaskResult
from typing import Dict

async def execute_rule(rule: Rule) -> Dict:
    """执行单条规则检测"""
    try:
        if rule.rule_type == "command":
            # 示例：执行系统命令检测
            result = subprocess.run(
                rule.params["command"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout + result.stderr
            is_compliant = result.returncode == rule.expected_result.get("expected_return_code", 0)
            
            # 检查输出是否包含指定内容
            if "must_contain" in rule.expected_result:
                if not re.search(rule.expected_result["must_contain"], output, re.IGNORECASE):
                    is_compliant = False
            if "must_not_contain" in rule.expected_result:
                if re.search(rule.expected_result["must_not_contain"], output, re.IGNORECASE):
                    is_compliant = False

        elif rule.rule_type == "registry":  # Windows注册表检测
            hive = getattr(winreg, rule.params["hive"])
            with winreg.OpenKey(hive, rule.params["key"]) as key:
                value, _ = winreg.QueryValueEx(key, rule.params["value_name"])
                is_compliant = str(value) == rule.expected_result["expected_value"]
                output = f"注册表值：{rule.params['key']}\\{rule.params['value_name']} = {value}"

        # 其他规则类型

        else:
            return {"error": f"不支持的规则类型: {rule.rule_type}", "compliant": False}

        return {"output": output, "compliant": is_compliant}

    except Exception as e:
        return {"error": str(e), "compliant": False}

async def run_security_checks(task_id: str):
    """异步执行所有规则检测"""
    from models import Task
    task = await Task.get(id=task_id)
    rules = await Rule.all()
    total = len(rules)
    await Task.filter(id=task_id).update(total=total, status="running")

    for idx, rule in enumerate(rules):
        result = await execute_rule(rule)
        await TaskResult.create(
            task_id=task_id,
            rule_id=rule.id,
            output=json.dumps(result),
            is_compliant=result["compliant"]
        )
        await Task.filter(id=task_id).update(progress=idx + 1)

    await Task.filter(id=task_id).update(status="completed")