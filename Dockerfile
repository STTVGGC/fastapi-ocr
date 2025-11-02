# 使用官方 Python 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# ✅ 安装系统依赖，解决 libGL.so.1 问题
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制整个 app 文件夹
COPY ./app /app

# 暴露端口
EXPOSE 8006

# 启动命令
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8006"]
