# 数据库初始化配置

from tortoise import Tortoise

async def init_baseline_db():
    await Tortoise.init(
        db_url="sqlite://database//baseline.db",
        modules={"models": ["baseline.database.models"]}
    )
    await Tortoise.generate_schemas()