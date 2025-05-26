# 数据库配置

from tortoise import Tortoise

async def init_db():
    await Tortoise.init(
        db_url="sqlite://database/security_check.db",
        modules={"models": ["models"]}
    )
    await Tortoise.generate_schemas()