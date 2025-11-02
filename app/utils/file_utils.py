import os
def save_file(path: str, data: bytes):
    # 自动创建目录（若不存在）
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as f:
        f.write(data)
