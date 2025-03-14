# web 服务器
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from tortoise.contrib.fastapi import register_tortoise
import os

from app import logger,app_config
from app.api.user import api_user
from app.api.system import api_system
from app.api.template import api_template
from app.api.file import api_file
from app.api.AI import api_AI
from app.utils.database import engine
from app.schemas.AI_chat import Base

#from wordease.api.user import api_user

logo_tmpl=r"""
----------------------------------------
            app已经运行
----------------------------------------
"""
mysql_config = app_config.mysql_config

def check_env():
    os.makedirs("data/", exist_ok=True)

# 以下是API的文档信息，FastAPI项目的基础配置
app = FastAPI(
    title="API",
    description="API模板",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)
# 初始化 Tortoise ORM（用于Python中与数据库的交互）
register_tortoise(
        app,
        config=mysql_config,
        generate_schemas=True,  # 开发环境可以生成表结构，生产环境建议关闭
        add_exception_handlers=True,  # 显示错误信息
    )
check_env()

@app.get("/")
async def root():
    return RedirectResponse(url="/template/index/")
    
# 允许跨域请求
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有方法
        allow_headers=["*"],  # 允许所有头
    )

# app.include_router()用于将路由添加到FastAPI应用中
app.include_router(api_user, prefix="/user", tags=["用户相关接口"])
app.include_router(api_system, prefix="/system", tags=["系统相关接口"])
app.include_router(api_template, prefix="/template", tags=["模板相关接口"])
app.include_router(api_file, prefix="/file", tags=["文件相关接口"])
app.include_router(api_AI, prefix="/AI", tags=["AI相关接口"])


if __name__ == '__main__':
    logger.info(logo_tmpl)
    Base.metadata.create_all(bind=engine) # 自动创建表
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    