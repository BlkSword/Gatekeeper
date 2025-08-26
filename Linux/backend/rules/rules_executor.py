# 规则执行引擎

import subprocess
import json
import re
import os
import hashlib
#import winreg  # Windows only
from rules.rules_models import Rule, TaskResult

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
            
            expected_result = rule.expected_result
            if isinstance(expected_result, str):
                try:
                    expected_result = json.loads(expected_result)
                except json.JSONDecodeError:
                    expected_result = eval(expected_result)
            
            if "must_contain" in expected_result:
                if not re.search(expected_result["must_contain"], output, re.IGNORECASE):
                    is_compliant = False
            if "must_not_contain" in expected_result:
                if re.search(expected_result["must_not_contain"], output, re.IGNORECASE):
                    is_compliant = False

        elif rule.rule_type == "file":
            expected_result = rule.expected_result
            if isinstance(expected_result, str):
                try:
                    expected_result = json.loads(expected_result)
                except json.JSONDecodeError:
                    expected_result = eval(expected_result)
            
            file_path = rule.params["path"]
            with open(file_path, "rb") as f:
                content = f.read()
            hash_func = getattr(hashlib, rule.params["hash_type"])
            file_hash = hash_func(content).hexdigest()
            is_compliant = file_hash == expected_result["expected_hash"]
            output = f"File check: {file_path}"

        elif rule.rule_type == "service":
            expected_result = rule.expected_result
            if isinstance(expected_result, str):
                try:
                    expected_result = json.loads(expected_result)
                except json.JSONDecodeError:
                    expected_result = eval(expected_result)
            
            # Linux 服务检查
            service_name = rule.params["service_name"]
            result = subprocess.run(
                f"systemctl is-active {service_name}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            is_compliant = expected_result["expected_status"] in result.stdout
            output = result.stdout + result.stderr

        elif rule.rule_type == "registry":
            pass

        elif rule.rule_type == "python_script":
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            script_path = rule.params["script_path"]
            args = rule.params.get("args", [])
            
            result = subprocess.run(
                ["python", script_path] + args,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout + result.stderr
            
            try:
                json_output = json.loads(output)
                # 两种格式解析
                checks = json_output.get("security_policy", {}).get("checks", [])
                if checks:  
                    is_compliant = all(check.get("status") is True for check in checks)
                    detailed_report = "\n".join([
                        f"{check.get('check_name', 'Unknown')}: {'Compliant' if check.get('status') else 'Non-compliant'}"
                        for check in checks
                    ]) if checks else "No checks found in response"
                else:  
                    is_compliant = json_output.get("status") is True
                    detailed_report = json_output.get("message", "No detailed report")
                
                output = f"Compliance Status: {'Compliant' if is_compliant else 'Non-compliant'}\n{detailed_report}"
                
            except json.JSONDecodeError as e:
                is_compliant = False
                output = f"JSON Parse Failed: {str(e)}\nRaw Output:\n{output}"
            except Exception as e:
                is_compliant = False
                output = f"Error processing response: {str(e)}\nRaw Output:\n{output}"  

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
    from rules.rules_models import Task
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

async def run_single_security_check(task_id: str, rule_name: str):
    """异步执行单个规则检测"""
    from rules.rules_models import Task
    task = await Task.get(id=task_id)
    
    # 查询指定名称的规则
    rule = await Rule.filter(name=rule_name).first()
    if not rule:
        await Task.filter(id=task_id).update(status="failed", total=1, progress=0)
        return
    
    await Task.filter(id=task_id).update(total=1, status="running")
    
    result = await execute_rule(rule)
    await TaskResult.create(
        task_id=task_id,
        rule_id=rule.id,
        output=json.dumps(result),
        is_compliant=result["compliant"]
    )
    await Task.filter(id=task_id).update(progress=1, status="completed")