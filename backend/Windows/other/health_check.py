import ctypes
import traceback
from fastapi.logger import logger
from fastapi.responses import JSONResponse


def get_health_check():
    try:
        has_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
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