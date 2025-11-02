项目名称
========

FastAPI + RapidOCR 练习项目

简介
----

这是一个基于 FastAPI 的 OCR（光学字符识别）演示服务，使用 rapidocr-onnxruntime 作为 OCR 引擎。项目提供文件上传、基于文件或字节流的 OCR 接口，以及一个健康检查接口。

主要功能
-------

- / -> 根路径，返回服务运行状态
- POST /api/upload -> 上传图片，返回保存的文件名与路径
- POST /api/ocr -> 对上传的图片（通过文件或 filename）执行 OCR，并返回识别文本
- GET /api/status -> 系统运行状态

仓库结构（摘要）
----------------

- app/main.py             应用入口
- app/routers/upload.py   上传路由
- app/routers/ocr.py      OCR 路由
- app/routers/status.py   系统状态路由
- app/services/ocr_service.py  OCR 服务封装，调用 rapidocr_onnxruntime
- app/utils/file_utils.py 保存文件的工具
- app/core/config.py     配置（读取 .env）
- requirements.txt       依赖清单

安装与快速运行（本地）
--------------------

1. 建议创建虚拟环境并激活（Windows cmd 示例）:

   python -m venv .venv
   .venv\Scripts\activate

2. 安装依赖：

   pip install -r requirements.txt

3. 运行服务（开发模式，自动重载）：

   uvicorn main:app --reload --host 127.0.0.1 --port 8006

4. 打开浏览器访问：

   http://127.0.0.1:8006

API 使用示例
-----------

1) 上传文件（curl 示例）

   curl -X POST "http://127.0.0.1:8006/api/upload" -F "file=@path_to_image.jpg"

返回示例：

   {"filename": "<uuid>.jpg", "path": "uploads/<uuid>.jpg"}

2) OCR（通过文件上传或通过 filename 引用）

- 通过上传文件：

   curl -X POST "http://127.0.0.1:8006/api/ocr" -F "file=@path_to_image.jpg"

- 通过已保存的 filename：

   curl -X POST "http://127.0.0.1:8006/api/ocr?filename=<uuid>.jpg"

返回示例：

   {"texts": ["识别到的文本1", "识别到的文本2"]}

配置（.env）
-----------

项目会读取根目录或环境中的以下变量：

- UPLOAD_DIR: 上传文件保存目录（默认 uploads）
- MODEL_PATH: rapidocr 模型目录（默认 models/rapidocr）
- LOG_LEVEL: 日志等级（默认 INFO）

Docker
------

仓库包含 `Dockerfile`，可以构建镜像并在容器中运行：

1. 构建镜像：

   docker build -t ocr-service .

2. 运行容器：

   docker run -p 8006:8006 ocr-service

或者使用提供的 `docker-compose.yml`（若已配置）：

   docker-compose up --build

常见问题与故障排查（重点：ImportError: ErrorWrapper）
-----------------------------------------------

你提到的错误：

ImportError: cannot import name 'ErrorWrapper' from 'fastapi._compat' (... site-packages ...)

分析与原因：

- 在我检查项目代码后（app 下所有模块），项目本身没有直接引用 `ErrorWrapper` 或 `fastapi._compat`。也就是说错误不是由你项目内的代码直接导入造成的，而是运行环境中某个已安装的第三方包在导入 FastAPI 的兼容层时尝试从 `fastapi._compat` 导入 `ErrorWrapper`，但当前安装的 FastAPI 版本并不提供这个符号或位置已变更。

- 通常这类错误由依赖版本不匹配引起（例如 FastAPI、Pydantic、Starlette 或某个第三方库之间的兼容性问题）。常见情形：某个库针对 FastAPI 的旧内部 API（私有模块）做了引用，但你的 FastAPI 是不同的版本。

定位与解决步骤（可执行）：

1. 查看完整错误栈（Traceback）找到是哪个模块/包在尝试导入 `ErrorWrapper`，这会直接指明“责任方”。

2. 查看当前环境中的包版本：

   pip show fastapi pydantic starlette python-multipart rapidocr-onnxruntime
   pip freeze > deps.txt

3. 常见可行修复（任选其一，视需求选择）：

   - 保守方案（降级/固定到兼容组合）：将 FastAPI 与 Pydantic 固定为兼容版本。例如（示例，请先在非生产环境中测试）：

     pip install "fastapi==0.95.2" "pydantic==1.10.12"

     说明：如果你的代码或其它依赖仍依赖 Pydantic v2，则不应降级 pydantic — 需要统一所有依赖到相容组合。

   - 激进方案（升级依赖到最新）：尝试升级 FastAPI 与其它包到最新稳定版：

     pip install -U fastapi pydantic starlette python-multipart

     注意：升级后某些使用 Pydantic v1 的库可能出现不兼容，需要同步升级或修改代码。

4. 如果不确定是哪一个包造成的，获取 traceback 并把顶层几行错误发给我，我可以帮你定位对应的包并给出精确的版本建议。

5. 快速检查（在你的环境里运行）：

   python - <<PY
   try:
       from fastapi._compat import ErrorWrapper
       print('Found ErrorWrapper in fastapi._compat')
   except Exception as e:
       import traceback
       traceback.print_exc()
   PY

   这会明确说明当前环境中该导入是否可用（还是会报错）以及完整的异常信息。

建议
----

- 最稳妥的方式是查看完整 traceback，锁定触发该导入的包，然后依照该包的文档选用兼容的 fastapi/pydantic 版本。不要随意修改 FastAPI 包内部代码。

- 在 `requirements.txt` 中使用明确的版本号（pin）以保证可重复性。例如：

  fastapi==0.95.2
  uvicorn==0.22.0
  python-multipart==0.0.6
  python-dotenv==1.1.1
  rapidocr-onnxruntime==0.1.0
  pillow==9.0.0

  （以上版本仅示例，请根据你的环境和测试结果进行调整并验证）

如需我更进一步帮助：
--------------------

- 如果你愿意，把出错的完整 Traceback 发给我（或粘贴到这里），我会基于 traceback 给出具体的修复命令和精确版本号建议。

- 若你想，我可以帮你自动生成一个带版本固定的 `requirements_pinned.txt` 并在本项目中替换或添加一个 `README` 中建议的版本范围。

---

如果你想现在就让我把 README 写入仓库（我已经完成）并再帮你生成 pinned requirements 或检查 traceback，请告诉我下一步操作。
