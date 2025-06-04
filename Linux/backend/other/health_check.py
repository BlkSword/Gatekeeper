import ctypes
import traceback
import os  # 新增 os 模块导入
from fastapi.logger import logger
from fastapi.responses import JSONResponse


def get_health_check():
    try:
        has_admin = os.geteuid() == 0
        return {
            "status": "ok",
            "has_admin_permission": has_admin  
        }
    except Exception as e:
        logger.error(f"健康检查权限验证失败: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Health check failed", "error": str(e)}
        )