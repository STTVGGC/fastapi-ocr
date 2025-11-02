import os
from dotenv import load_dotenv

# 读取 .env 文件
load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MODEL_PATH = os.getenv("MODEL_PATH", "models/rapidocr")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
