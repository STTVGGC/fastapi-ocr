# main.py
import uvicorn
from fastapi import FastAPI
from routers import upload, ocr, status, bill

# 导入数据库基础类和引擎
from app.database import Base, engine, AsyncSessionLocal
from app.models.user import User

# import pymysql
# pymysql.install_as_MySQLdb()

# # -------------------------
# # ★ 创建数据库中的所有表（很关键）
# # -------------------------
# # Base.metadata.create_all 会根据你所有 models/*.py 中的类
# # 自动生成对应的数据库表
# print("⏳ 正在根据模型创建数据库表...")
# Base.metadata.create_all(bind=engine)
# print("✅ 数据库表创建成功！")

app = FastAPI(title="OCR API Service")

# 注册路由
app.include_router(upload.router, prefix="/api")
app.include_router(ocr.router, prefix="/api")
app.include_router(status.router, prefix="/api")
app.include_router(bill.router, prefix="/api")


@app.get("/")
def home():
    return {"message": "OCR API is running ✅"}


# # -------------------------
# # ★ 程序启动时插入一个默认管理员用户（示例）
# # -------------------------
# db = AsyncSessionLocal()
# try:
#     existing = db.query(User).filter_by(email="admin@test.com").first()
#     if existing:
#         print(f"ℹ️ 管理员已存在，ID: {existing.id}")
#     else:
#         new_user = User(username="admin", email="admin@test.com")
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
#         print(f"✅ 已创建管理员用户，ID: {new_user.id}")
# finally:
#     db.close()


# -------------------------
# ★ API 启动入口
# -------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8006, reload=True)
