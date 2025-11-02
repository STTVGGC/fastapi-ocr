import uvicorn
from fastapi import FastAPI
from routers import upload, ocr, status

app = FastAPI(title="OCR API Service")

app.include_router(upload.router, prefix="/api")
app.include_router(ocr.router, prefix="/api")
app.include_router(status.router, prefix="/api")
@app.get("/")
def home():
    return {"message": "OCR API is running ✅"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8006, reload=True)