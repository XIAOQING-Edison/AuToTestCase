from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.test_case import router as test_case_router
from api.config import router as config_router
from api.ocr import router as ocr_router

app = FastAPI(title="AuToTestCase API", description="API for generating test cases from requirements")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境中允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # 允许前端访问Content-Disposition头，用于文件下载
)

# 注册路由
app.include_router(test_case_router, prefix="/api/test-cases", tags=["test-cases"])
app.include_router(config_router, prefix="/api/config", tags=["config"])
app.include_router(ocr_router, prefix="/api/ocr", tags=["ocr"])

@app.get("/")
def read_root():
    return {"message": "Welcome to AuToTestCase API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 