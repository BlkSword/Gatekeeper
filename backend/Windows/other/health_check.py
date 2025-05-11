import ctypes
import traceback
from fastapi.logger import logger
from fastapi.responses import JSONResponse


def get_health_check():
    try:
        # 检查管理员权限（Windows系统API）
        has_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
        return {
            "status": "ok",
            "has_admin_permission": has_admin  # 新增权限状态字段
        }
    except Exception as e:
        logger.error(f"健康检查权限验证失败: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Health check failed", "error": str(e)}
        )