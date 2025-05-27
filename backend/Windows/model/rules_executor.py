# 规则执行引擎

import subprocess
import json
import re
import hashlib
import winreg  # Windows only
from model.models import Rule, TaskResult

async def execute_rule(rule: Rule) -> dict:
    try:
        if rule.rule_type == "command":
            result = subprocess.run(
                rule.params["command"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout + result.stderr
            is_compliant = result.returncode == 0
            
            if "must_contain" in rule.expected_result:
                if not re.search(rule.expected_result["must_contain"], output, re.IGNORECASE):
                    is_compliant = False
            if "must_not_contain" in rule.expected_result:
                if re.search(rule.expected_result["must_not_contain"], output, re.IGNORECASE):
                    is_compliant = False

        elif rule.rule_type == "file":
            file_path = rule.params["path"]
            with open(file_path, "rb") as f:
                content = f.read()
            hash_func = getattr(hashlib, rule.params["hash_type"])
            file_hash = hash_func(content).hexdigest()
            is_compliant = file_hash == rule.expected_result["expected_hash"]
            output = f"File check: {file_path}"

        elif rule.rule_type == "service":
            # Linux 服务检查（systemctl）
            service_name = rule.params["service_name"]
            result = subprocess.run(
                f"systemctl is-active {service_name}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            is_compliant = rule.expected_result["expected_status"] in result.stdout
            output = result.stdout + result.stderr

        elif rule.rule_type == "registry":
            # Windows 注册表检查
            hive = getattr(winreg, rule.params["hive"])
            key = winreg.OpenKey(hive, rule.params["key"])
            value, _ = winreg.QueryValueEx(key, rule.params["value_name"])
            is_compliant = value == rule.expected_result["expected_value"]
            output = f"Registry check: {rule.params['key']}\\{rule.params['value_name']}"

        else:
            return {"error": f"Unsupported rule type: {rule.rule_type}"}

        return {
            "output": output,
            "compliant": is_compliant
        }

    except Exception as e:
        return {"error": str(e), "compliant": False}

async def run_security_checks(task_id: str):
    """异步执行所有规则检测"""
    from model.models import Task
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