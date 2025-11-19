# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库连接URL格式
# mysql+pymysql://用户名:密码@主机:端口/数据库名
SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://root:A19356756837@localhost:3306/ocr_db"

# 创建引擎
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)

# 创建Session工厂
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession,expire_on_commit=False)

# 声明模型基类
Base = declarative_base()

# def get_db():
#     """依赖注入：获取数据库会话"""
    # db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()
# 异步依赖注入
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session